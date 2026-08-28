from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
WAREHOUSE_DIR = ROOT / "data" / "warehouse"
WAREHOUSE_PATH = WAREHOUSE_DIR / "omop_mart.duckdb"
REPORTS_DIR = ROOT / "reports"
