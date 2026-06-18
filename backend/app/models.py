from sqlalchemy import BigInteger, Column, DateTime, Float, Index, Integer, String, func
from sqlalchemy.dialects import mysql

from app.database import Base

#数据库模型 / ORM 模型
"""
数据库表 traffic_log  <->  Python 类 TrafficLog
数据库中的一行记录       <->  Python 中的一个 TrafficLog 对象
数据库中的一列字段       <->  TrafficLog 类上的一个属性
"""
class TrafficLog(Base):
    __tablename__ = "traffic_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    src_ip = Column(String(45), nullable=False)
    src_port = Column(Integer)
    dst_ip = Column(String(45), nullable=False)
    dst_port = Column(Integer)
    protocol = Column(String(10))
    packet_size = Column(Integer)
    duration = Column(Float)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SrcIpAly(Base):
    __tablename__ = "src_ip_aly"

    src_ip = Column(String(45), primary_key=True)
    src_ip_hash = Column(mysql.BIGINT(unsigned=True), nullable=False)
    count = Column(BigInteger, nullable=False, default=0)
    total_bytes = Column(BigInteger, nullable=False, default=0)

    __table_args__ = (
        Index("idx_src_ip_hash_ip", "src_ip_hash", "src_ip"),
        Index("idx_total_bytes", "total_bytes"),
    )
