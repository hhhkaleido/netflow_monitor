import csv
import threading
import time
from queue import Queue
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app import crud
from app.config import settings
from app.database import SessionLocal
from app.services.import_service import _resolve_csv_path
from app.utils.csv_parser import parse_traffic_row


STOP_SIGNAL = object()


def import_csv_file_concurrently(csv_path: str) -> dict[str, Any]:
    path = _resolve_csv_path(csv_path)
    start_time = time.perf_counter()
    worker_count = max(1, settings.IMPORT_WORKER_COUNT)
    batch_size = max(1, settings.BATCH_SIZE)

    raw_queue: Queue[dict[str, Any] | object] = Queue()
    record_queue: Queue[dict[str, Any] | object] = Queue()
    stats_lock = threading.Lock()
    stats = {
        "success_count": 0,
        "failed_count": 0,
    }
    errors: list[BaseException] = []

    def add_success(count: int) -> None:
        with stats_lock:
            stats["success_count"] += count

    def add_failed(count: int = 1) -> None:
        with stats_lock:
            stats["failed_count"] += count

    def worker() -> None:
        while True:
            row = raw_queue.get()
            try:
                if row is STOP_SIGNAL:
                    return

                try:
                    record_queue.put(parse_traffic_row(row))
                except (ValueError, TypeError):
                    add_failed()
            finally:
                raw_queue.task_done()

    def writer() -> None:
        db = SessionLocal()
        batch: list[dict[str, Any]] = []
        try:
            while True:
                record = record_queue.get()
                try:
                    if record is STOP_SIGNAL:
                        break

                    batch.append(record)
                    if len(batch) >= batch_size:
                        add_success(crud.batch_insert_traffic_logs(db, batch))
                        batch.clear()
                finally:
                    record_queue.task_done()

            if batch:
                add_success(crud.batch_insert_traffic_logs(db, batch))
        except SQLAlchemyError as exc:
            db.rollback()
            errors.append(exc)
        finally:
            db.close()

    workers = [
        threading.Thread(target=worker, name=f"csv-import-worker-{index + 1}")
        for index in range(worker_count)
    ]
    writer_thread = threading.Thread(target=writer, name="csv-import-writer")

    writer_thread.start()
    for thread in workers:
        thread.start()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            raw_queue.put(row)

    for _ in workers:
        raw_queue.put(STOP_SIGNAL)

    for thread in workers:
        thread.join()

    record_queue.put(STOP_SIGNAL)
    writer_thread.join()

    if errors:
        raise errors[0]

    elapsed_seconds = round(time.perf_counter() - start_time, 3)
    return {
        "csv_path": str(path),
        "success_count": stats["success_count"],
        "failed_count": stats["failed_count"],
        "elapsed_seconds": elapsed_seconds,
        "worker_count": worker_count,
        "batch_size": batch_size,
    }
