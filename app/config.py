from pathlib import Path
import os, sys
APP_NAME='InventoryChecker'; APP_VERSION='1.0.0'
BASE_DIR=Path(os.getenv('LOCALAPPDATA', Path.home()/'.local/share'))/APP_NAME
DB_PATH=BASE_DIR/'inventory_checker.db'; LOG_DIR=BASE_DIR/'logs'; BACKUP_DIR=BASE_DIR/'backups'
for p in (BASE_DIR,LOG_DIR,BACKUP_DIR): p.mkdir(parents=True,exist_ok=True)
def resource_path(rel):
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1])); return root/rel
