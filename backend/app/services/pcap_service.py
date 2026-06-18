from pathlib import Path
from typing import Any
import importlib.util

from sqlalchemy.orm import Session
from app.config import settings
from app.services.import_service import import_csv_file


def load_extract_pcap_to_csv():
    script_path = settings.PCAP_EXTRACT_SCRIPT
    if not script_path.exists():
        raise FileNotFoundError(f"PCAP extract script does not exist: {script_path}")

    spec = importlib.util.spec_from_file_location("legacy_extract_pcap", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load PCAP extract script: {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        return module.extract_pcap_to_csv
    except AttributeError as exc:
        raise ImportError("extract_pcap_to_csv function was not found") from exc


def import_pcap_file(
    db: Session,
    pcap_path: str,
    output_csv_path: str | None = None,
) -> dict[str, Any]:
    resolved_pcap_path = resolve_pcap_path(pcap_path)
    resolved_output_csv_path = resolve_output_csv_path(output_csv_path)
    converted_csv_path = convert_pcap_to_csv(resolved_pcap_path, resolved_output_csv_path)
    import_result = import_csv_file(db, str(converted_csv_path))

    return {
        "pcap_path": str(resolved_pcap_path),
        "csv_path": str(converted_csv_path),
        **import_result,
    }


def resolve_pcap_path(pcap_path: str) -> Path:
    path = Path(pcap_path)
    if not path.is_absolute():
        path = settings.PROJECT_ROOT / path
    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"PCAP file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"PCAP path is not a file: {path}")
    if path.suffix.lower() not in {".pcap", ".pcapng"}:
        raise ValueError(f"file is not a PCAP/PCAPNG: {path}")

    return path


def resolve_output_csv_path(output_csv_path: str | None = None) -> Path:
    path = Path(output_csv_path) if output_csv_path else settings.DATA_DIR / "extracted_network.csv"
    if not path.is_absolute():
        path = settings.PROJECT_ROOT / path
    path = path.resolve()

    if path.exists() and not path.is_file():
        raise ValueError(f"CSV path is not a file: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"file is not a CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def convert_pcap_to_csv(pcap_path: Path, output_csv_path: Path) -> Path:
    extract_pcap_to_csv = load_extract_pcap_to_csv()
    extract_pcap_to_csv(str(pcap_path), str(output_csv_path))
    return output_csv_path
