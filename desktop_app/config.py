from pathlib import Path


APP_NAME = "QuickNote"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "quicknote.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
