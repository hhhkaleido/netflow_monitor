import os
from pathlib import Path
from urllib.parse import quote_plus


class Settings:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DATA_DIR = PROJECT_ROOT / "data"
    PCAP_EXTRACT_SCRIPT = PROJECT_ROOT / "py" / "extract_pcap.py"

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "netflow_monitor")

    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
    IMPORT_WORKER_COUNT = int(os.getenv("IMPORT_WORKER_COUNT", "4"))

    @property
    def database_url(self) -> str:
        user = quote_plus(self.MYSQL_USER)
        password = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )


settings = Settings()
