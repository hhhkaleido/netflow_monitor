from datetime import datetime
from typing import Any


PROTOCOL_MAP = {
    "1": "ICMP",
    "6": "TCP",
    "17": "UDP",
    "ICMP": "ICMP",
    "TCP": "TCP",
    "UDP": "UDP",
}


FIELD_ALIASES = {
    "src_ip": ("src_ip", "Source", "source", "src", "SrcIP"),
    "dst_ip": ("dst_ip", "Destination", "destination", "dst", "DstIP"),
    "protocol": ("protocol", "Protocol"),
    "src_port": ("src_port", "SrcPort", "source_port"),
    "dst_port": ("dst_port", "DstPort", "destination_port"),
    "packet_size": ("packet_size", "DataSize", "data_size", "size", "bytes"),
    "duration": ("duration", "Duration"),
    "created_at": ("created_at", "CreatedAt", "timestamp", "time"),
}


def parse_traffic_row(row: dict[str, Any]) -> dict[str, Any]:
    src_ip = _required_string(row, "src_ip")
    dst_ip = _required_string(row, "dst_ip")

    record = {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": _normalize_protocol(_optional_string(row, "protocol")),
        "src_port": _optional_int(row, "src_port"),
        "dst_port": _optional_int(row, "dst_port"),
        "packet_size": _optional_int(row, "packet_size") or 0,
        "duration": _optional_float(row, "duration"),
    }

    created_at = _optional_datetime(row, "created_at")
    if created_at is not None:
        record["created_at"] = created_at

    return record


def _get_value(row: dict[str, Any], canonical_name: str) -> Any:
    for alias in FIELD_ALIASES[canonical_name]:
        if alias in row:
            return row[alias]
    return None


def _optional_string(row: dict[str, Any], canonical_name: str) -> str | None:
    value = _get_value(row, canonical_name)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _required_string(row: dict[str, Any], canonical_name: str) -> str:
    value = _optional_string(row, canonical_name)
    if value is None:
        raise ValueError(f"missing required field: {canonical_name}")
    return value


def _optional_int(row: dict[str, Any], canonical_name: str) -> int | None:
    value = _optional_string(row, canonical_name)
    if value is None:
        return None
    return int(float(value))


def _optional_float(row: dict[str, Any], canonical_name: str) -> float | None:
    value = _optional_string(row, canonical_name)
    if value is None:
        return None
    return float(value)


def _optional_datetime(row: dict[str, Any], canonical_name: str) -> datetime | None:
    value = _optional_string(row, canonical_name)
    if value is None:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid datetime: {value}") from exc


def _normalize_protocol(value: str | None) -> str:
    if value is None:
        return "OTHER"
    return PROTOCOL_MAP.get(value.upper(), "OTHER")
