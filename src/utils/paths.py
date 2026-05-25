from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARTIFACT_DIR = ROOT_DIR / "artifacts"
MODEL_DIR = ARTIFACT_DIR / "models"
LOG_DIR = ARTIFACT_DIR / "logs"
REPORT_ARTIFACT_DIR = ARTIFACT_DIR / "reports"


def ensure_project_directories() -> None:
    for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR, LOG_DIR, REPORT_ARTIFACT_DIR]:
        path.mkdir(parents=True, exist_ok=True)
