from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ProtocolStatsResponse,
    SrcIpAlyResponse,
    SummaryResponse,
    TopDstPortResponse,
    TopSrcIpResponse,
)
from app.services.stats_service import (
    get_protocol_stats,
    get_src_ip_aly_stats,
    get_summary_stats,
    get_top_dst_port_stats,
    get_top_src_ip_stats,
)


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/top-src-ip", response_model=TopSrcIpResponse)
def get_top_src_ip_api(
    limit: int = Query(10, ge=1, le=100, description="Number of source IP items to return"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return get_top_src_ip_stats(db=db, limit=limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database stats query failed: {exc}") from exc


@router.get("/src-ip-aly", response_model=SrcIpAlyResponse)
def get_src_ip_aly_api(
    src_ip: str = Query(..., min_length=1, max_length=45, description="Source IP to lookup by hash index"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return get_src_ip_aly_stats(db=db, src_ip=src_ip)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database hash index query failed: {exc}") from exc


@router.get("/top-dst-port", response_model=TopDstPortResponse)
def get_top_dst_port_api(
    limit: int = Query(10, ge=1, le=100, description="Number of destination port items to return"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return get_top_dst_port_stats(db=db, limit=limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database stats query failed: {exc}") from exc


@router.get("/protocol-stats", response_model=ProtocolStatsResponse)
def get_protocol_stats_api(db: Session = Depends(get_db)) -> dict:
    try:
        return get_protocol_stats(db=db)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database stats query failed: {exc}") from exc


@router.get("/summary", response_model=SummaryResponse)
def get_summary_api(db: Session = Depends(get_db)) -> dict:
    try:
        return get_summary_stats(db=db)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"database stats query failed: {exc}") from exc
