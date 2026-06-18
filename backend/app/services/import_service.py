import csv
import time
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.utils.csv_parser import parse_traffic_row


def import_csv_file(db: Session, csv_path: str) -> dict[str, Any]:
    path = _resolve_csv_path(csv_path)
    start_time = time.perf_counter()
    success_count = 0
    failed_count = 0
    batch: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                batch.append(parse_traffic_row(row))
            except (ValueError, TypeError):
                failed_count += 1
                continue

            if len(batch) >= settings.BATCH_SIZE:
                success_count += crud.batch_insert_traffic_logs(db, batch)
                batch.clear()

    if batch:
        success_count += crud.batch_insert_traffic_logs(db, batch)

    elapsed_seconds = round(time.perf_counter() - start_time, 3)
    return {
        "csv_path": str(path),
        "success_count": success_count,
        "failed_count": failed_count,
        "elapsed_seconds": elapsed_seconds,
    }


def _resolve_csv_path(csv_path: str) -> Path:
    path = Path(csv_path)
    if not path.is_absolute():
        path = settings.PROJECT_ROOT / path
    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"CSV file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"CSV path is not a file: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"file is not a CSV: {path}")

    return path
