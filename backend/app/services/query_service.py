import time
from typing import Any

from sqlalchemy.orm import Session

from app import crud


def search_traffic_logs(
    db: Session,
    src_ip: str | None = None,
    dst_ip: str | None = None,
    limit: int = 20
) -> dict[str, Any]:
    start_time = time.perf_counter()

    records = crud.query_traffic_logs(
        db=db,
        src_ip=src_ip,
        dst_ip=dst_ip,
        limit=limit,
    )
    elapsed_time = round(time.perf_counter() - start_time, 3)
    
    return {
        "status": "success",
        "count": len(records),
        "elapsed_seconds": elapsed_time,
        "data": records,
    }


def get_recent_traffic_logs(
    db: Session,
    limit: int = 20
) -> dict[str, Any]:
    start_time = time.perf_counter()

    records = crud.query_recent_traffic_logs(db=db, limit=limit)
    elapsed_time = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "count": len(records),
        "elapsed_seconds": elapsed_time,
        "data": records,
    }
