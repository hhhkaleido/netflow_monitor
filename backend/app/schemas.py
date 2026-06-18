from datetime import datetime

from pydantic import BaseModel

#接口模型 / Pydantic 模型 / 响应模型
class TrafficLogResponse(BaseModel):
    id: int
    src_ip: str
    src_port: int | None = None
    dst_ip: str
    dst_port: int | None = None
    protocol: str | None = None
    packet_size: int | None = None
    duration: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrafficSearchResponse(BaseModel):
    status: str
    count: int
    elapsed_seconds: float
    data: list[TrafficLogResponse]


class TopSrcIpItem(BaseModel):
    src_ip: str
    count: int
    total_bytes: int


class TopSrcIpResponse(BaseModel):
    status: str
    count: int
    elapsed_seconds: float
    data: list[TopSrcIpItem]


class SrcIpAlyItem(BaseModel):
    src_ip: str
    src_ip_hash: int
    count: int
    total_bytes: int


class SrcIpAlyResponse(BaseModel):
    status: str
    found: bool
    elapsed_seconds: float
    data: SrcIpAlyItem | None = None


class TopDstPortItem(BaseModel):
    dst_port: int | None = None
    count: int
    total_bytes: int


class TopDstPortResponse(BaseModel):
    status: str
    count: int
    elapsed_seconds: float
    data: list[TopDstPortItem]


class ProtocolStatItem(BaseModel):
    protocol: str
    count: int
    total_bytes: int


class ProtocolStatsResponse(BaseModel):
    status: str
    count: int
    elapsed_seconds: float
    data: list[ProtocolStatItem]


class SummaryData(BaseModel):
    total_records: int
    total_bytes: int
    unique_src_ips: int
    unique_dst_ips: int


class SummaryResponse(BaseModel):
    status: str
    elapsed_seconds: float
    data: SummaryData
