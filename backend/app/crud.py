from sqlalchemy import func, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from app.models import SrcIpAly, TrafficLog


FNV1A_64_OFFSET_BASIS = 0xCBF29CE484222325
FNV1A_64_PRIME = 0x100000001B3
UINT64_MASK = 0xFFFFFFFFFFFFFFFF


def calculate_src_ip_hash(src_ip: str) -> int:
    hash_value = FNV1A_64_OFFSET_BASIS
    for byte in src_ip.encode("utf-8"):
        hash_value ^= byte
        hash_value = (hash_value * FNV1A_64_PRIME) & UINT64_MASK
    return hash_value


def batch_insert_traffic_logs(db: Session, records: list[dict]) -> int:
    if not records:
        return 0

    #TrafficLog是Python->MySQL变量转换，records为真实数据#
    db.bulk_insert_mappings(TrafficLog, records)
    upsert_src_ip_aly_from_records(db, records)
    db.commit()
    return len(records)


def upsert_src_ip_aly_from_records(db: Session, records: list[dict]) -> int:
    aggregated: dict[str, dict] = {}

    for record in records:
        src_ip = record.get("src_ip")
        if not src_ip:
            continue

        item = aggregated.setdefault(
            src_ip,
            {
                "src_ip": src_ip,
                "src_ip_hash": calculate_src_ip_hash(src_ip),
                "count": 0,
                "total_bytes": 0,
            },
        )
        item["count"] += 1
        item["total_bytes"] += int(record.get("packet_size") or 0)

    if not aggregated:
        return 0

    rows = list(aggregated.values())
    statement = insert(SrcIpAly).values(rows)
    update_statement = statement.on_duplicate_key_update(
        count=SrcIpAly.count + statement.inserted["count"],
        total_bytes=SrcIpAly.total_bytes + statement.inserted["total_bytes"],
        src_ip_hash=statement.inserted["src_ip_hash"],
    )
    db.execute(update_statement)
    return len(rows)


def get_src_ip_aly_by_hash(db: Session, src_ip: str) -> dict | None:
    src_ip_hash = calculate_src_ip_hash(src_ip)
    row = (
        db.query(SrcIpAly)
        .filter(SrcIpAly.src_ip_hash == src_ip_hash, SrcIpAly.src_ip == src_ip)
        .first()
    )

    if row is None:
        return None

    return {
        "src_ip": row.src_ip,
        "src_ip_hash": int(row.src_ip_hash),
        "count": int(row.count),
        "total_bytes": int(row.total_bytes),
    }


def clear_netflow_database(db: Session) -> dict:
    db.execute(text("TRUNCATE TABLE src_ip_aly"))
    db.execute(text("TRUNCATE TABLE traffic_log"))
    db.commit()

    return {
        "cleared_tables": ["src_ip_aly", "traffic_log"],
    }


def sync_src_ip_aly_from_traffic_log(db: Session) -> dict:
    db.execute(text("TRUNCATE TABLE src_ip_aly"))

    rows = (
        db.query(
            TrafficLog.src_ip.label("src_ip"),
            func.count(TrafficLog.id).label("count"),
            func.coalesce(func.sum(TrafficLog.packet_size), 0).label("total_bytes"),
        )
        .group_by(TrafficLog.src_ip)
        .all()
    )

    mappings = [
        {
            "src_ip": row.src_ip,
            "src_ip_hash": calculate_src_ip_hash(row.src_ip),
            "count": int(row.count),
            "total_bytes": int(row.total_bytes or 0),
        }
        for row in rows
    ]

    if mappings:
        db.bulk_insert_mappings(SrcIpAly, mappings)

    db.commit()
    return {
        "synced_src_ip_count": len(mappings),
    }

def query_traffic_logs(
    db: Session,
    src_ip: str | None = None,
    dst_ip: str | None = None,
    limit: int = 20
) -> list[TrafficLog]:
    if src_ip is None and dst_ip is None:
        return []

    query = db.query(TrafficLog)
    if src_ip is not None:
        query = query.filter(TrafficLog.src_ip == src_ip,)
    
    if dst_ip is not None:
        query = query.filter(TrafficLog.dst_ip == dst_ip)

    return(
        query
        .order_by(TrafficLog.created_at.desc())
        .limit(limit)
        .all()
    ) 

def query_recent_traffic_logs(db: Session, limit: int = 20) -> list[TrafficLog]:
    return(
        db.query(TrafficLog)
        .order_by(TrafficLog.created_at.desc(), TrafficLog.id.desc())
        .limit(limit)
        .all()
    )

"""
GET /stats/top-src-ip
GET /stats/top-dst-port
GET /stats/protocol-stats
GET /stats/summary
"""
def get_top_src_ip(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(
            TrafficLog.src_ip.label("src_ip"),
            func.count(TrafficLog.id).label("count"),
            func.coalesce(func.sum(TrafficLog.packet_size), 0).label("total_bytes"),
        )
        .group_by(TrafficLog.src_ip)
        .order_by(func.coalesce(func.sum(TrafficLog.packet_size), 0).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "src_ip": row.src_ip,
            "count": int(row.count),
            "total_bytes": int(row.total_bytes or 0),
        }
        for row in rows
    ]

def get_top_dst_port(
    db:Session,
    limit: int =10
):
    rows = (
        db.query(
            TrafficLog.dst_port.label("dst_port"),
            func.count(TrafficLog.id).label("count"),
            func.coalesce(func.sum(TrafficLog.packet_size), 0).label("total_bytes")
        )
        .group_by(TrafficLog.dst_port)
        .order_by(func.coalesce(func.sum(TrafficLog.packet_size), 0).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "dst_port":row.dst_port,
            "count":int(row.count),
            "total_bytes":int(row.total_bytes)
        }
        for row in rows
    ]


def get_protocol_stats(db: Session) -> list[dict]:
    rows = (
        db.query(
            TrafficLog.protocol.label("protocol"),
            func.count(TrafficLog.id).label("count"),
            func.coalesce(func.sum(TrafficLog.packet_size), 0).label("total_bytes"),
        )
        .group_by(TrafficLog.protocol)
        .order_by(func.count(TrafficLog.id).desc())
        .all()
    )

    return [
        {
            "protocol": row.protocol or "UNKNOWN",
            "count": int(row.count),
            "total_bytes": int(row.total_bytes or 0),
        }
        for row in rows
    ]


def get_traffic_summary(db: Session) -> dict:
    row = db.query(
        func.count(TrafficLog.id).label("total_records"),
        func.coalesce(func.sum(TrafficLog.packet_size), 0).label("total_bytes"),
        func.count(func.distinct(TrafficLog.src_ip)).label("unique_src_ips"),
        func.count(func.distinct(TrafficLog.dst_ip)).label("unique_dst_ips"),
    ).one()

    return {
        "total_records": int(row.total_records or 0),
        "total_bytes": int(row.total_bytes or 0),
        "unique_src_ips": int(row.unique_src_ips or 0),
        "unique_dst_ips": int(row.unique_dst_ips or 0),
    }
