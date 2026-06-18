import time
from typing import Any

from sqlalchemy.orm import Session

from app import crud


def get_top_src_ip_stats(db: Session, limit: int = 10) -> dict[str, Any]:
    start_time = time.perf_counter()

    rows = crud.get_top_src_ip(db=db, limit=limit)
    elapsed_time = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "count": len(rows),
        "elapsed_seconds": elapsed_time,
        "data": rows,
    }


def get_src_ip_aly_stats(db: Session, src_ip: str) -> dict[str, Any]:
    start_time = time.perf_counter()

    data = crud.get_src_ip_aly_by_hash(db=db, src_ip=src_ip)
    elapsed_time = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "found": data is not None,
        "elapsed_seconds": elapsed_time,
        "data": data,
    }


def get_top_dst_port_stats(db: Session, limit: int = 10) -> dict[str, Any]:
    start_time = time.perf_counter()

    rows = crud.get_top_dst_port(db=db, limit=limit)
    elapsed_time = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "count": len(rows),
        "elapsed_seconds": elapsed_time,
        "data": rows,
    }


def get_protocol_stats(db: Session) -> dict[str, Any]:
    start_time = time.perf_counter()

    rows = crud.get_protocol_stats(db=db)
    elapsed_time = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "count": len(rows),
        "elapsed_seconds": elapsed_time,
        "data": rows,
    }


def get_summary_stats(db: Session) -> dict[str, Any]:
    start_time = time.perf_counter()

    summary = crud.get_traffic_summary(db=db)
    elapsed_time = round(time.perf_counter() - start_time, 3)

    return {
        "status": "success",
        "elapsed_seconds": elapsed_time,
        "data": summary,
    }
