from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import TrafficSearchResponse
from app.database import get_db
from app.services.concurrent_import import import_csv_file_concurrently
from app.services.import_service import import_csv_file
from app.services.pcap_service import import_pcap_file
from app.services.query_service import get_recent_traffic_logs, search_traffic_logs
router = APIRouter(prefix="/traffic", tags=["traffic"])

"""
路由调用链：
1.路由装饰器 @router.method
2.装饰器函数，直接调用services
3.services记录时间，使用crud中的函数返回dict
"""

@router.post("/import")
def import_traffic_csv(
    csv_path: str = Query(..., description="CSV file path, for example data/network_data.csv"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return import_csv_file(db, csv_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"database import failed: {exc}") from exc


@router.post("/import-concurrent")
def import_traffic_csv_concurrent(
    csv_path: str = Query(..., description="CSV file path, for example data/network_data.csv"),
) -> dict:
    try:
        return import_csv_file_concurrently(csv_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database import failed: {exc}") from exc


@router.post("/import-pcap")
def import_traffic_pcap(
    pcap_path: str = Query(..., description="PCAP/PCAPNG file path, for example data/my_traffic.pcap"),
    output_csv_path: str | None = Query(None, description="Optional output CSV path"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return import_pcap_file(db, pcap_path, output_csv_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=f"pcap extract module load failed: {exc}") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"database import failed: {exc}") from exc


@router.get("/search", response_model = TrafficSearchResponse)
def search_traffic_logs_api(
    src_ip: str | None = Query(None, description="Source IP address"),
    dst_ip: str | None = Query(None, description="Destination IP address"),
    limit: int = Query(20, ge = 1, le = 100, description="Number of results to return"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return search_traffic_logs(
            db=db,
            src_ip=src_ip,
            dst_ip=dst_ip,
            limit=limit,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database search failed: {exc}") from exc
    
@router.get("/recent", response_model = TrafficSearchResponse)
def get_recent_traffic_logs_api(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge = 1, le = 100, description="Number of results to return")
):
    try:
        return get_recent_traffic_logs(db=db, limit=limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database search failed: {exc}") from exc 
