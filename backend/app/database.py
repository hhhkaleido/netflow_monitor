from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

#负责维护数据库连接池
engine = create_engine(
    settings.database_url,
    connect_args={"connect_timeout": 5},
    pool_pre_ping=True,
    pool_recycle=3600,
)

#创建数据库会话
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
