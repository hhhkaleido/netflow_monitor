import time
from typing import Any

from sqlalchemy.orm import Session

from app import crud


def clear_database(db: Session) -> dict[str, Any]:
    start_time = time.perf_counter()

    result = crud.clear_netflow_database(db)
    elapsed_seconds = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "elapsed_seconds": elapsed_seconds,
        **result,
    }


def sync_src_ip_aly(db: Session) -> dict[str, Any]:
    start_time = time.perf_counter()

    result = crud.sync_src_ip_aly_from_traffic_log(db)
    elapsed_seconds = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "elapsed_seconds": elapsed_seconds,
        **result,
    }
