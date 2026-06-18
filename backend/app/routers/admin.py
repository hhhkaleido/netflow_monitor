from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.admin_service import clear_database, sync_src_ip_aly


router = APIRouter(prefix="/admin", tags=["admin"])

"""
@router.delete("/database")
def clear_database_api(db: Session = Depends(get_db)) -> dict:
    try:
        return clear_database(db=db)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"database clear failed: {exc}") from exc


@router.post("/src-ip-aly/sync")
def sync_src_ip_aly_api(db: Session = Depends(get_db)) -> dict:
    try:
        return sync_src_ip_aly(db=db)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"src_ip_aly sync failed: {exc}") from exc
"""