import sqlite3, json
from contextlib import contextmanager
from datetime import datetime
from app.config import DB_PATH
SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,project_date TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,inventory_path TEXT,inventory_sheet TEXT,label_column TEXT,header_row INTEGER DEFAULT 1,archived INTEGER DEFAULT 0,normalization_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,row_no INTEGER,original_label TEXT,normalized_label TEXT NOT NULL,row_json TEXT NOT NULL,FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS idx_inventory_project_label ON inventory(project_id,normalized_label);
CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,entered_label TEXT,normalized_label TEXT,status TEXT NOT NULL,scanned_at TEXT NOT NULL,source TEXT NOT NULL,notes TEXT DEFAULT '',deleted INTEGER DEFAULT 0,FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS idx_scans_project_label ON scans(project_id,normalized_label,deleted);
CREATE TABLE IF NOT EXISTS imports(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,file_path TEXT,sheet_name TEXT,column_name TEXT,imported_at TEXT NOT NULL,total_rows INTEGER,valid_rows INTEGER,empty_rows INTEGER,invalid_rows INTEGER,duplicate_rows INTEGER,FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
'''
class Database:
 def __init__(self,path=DB_PATH): self.path=str(path); self.init()
 @contextmanager
 def conn(self):
  c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
  try: yield c; c.commit()
  finally: c.close()
 def init(self):
  with self.conn() as c: c.executescript(SCHEMA)
 def execute(self,sql,p=()):
  with self.conn() as c: return c.execute(sql,p).lastrowid
 def query(self,sql,p=()):
  with self.conn() as c: return [dict(x) for x in c.execute(sql,p).fetchall()]
 def one(self,sql,p=()):
  r=self.query(sql,p); return r[0] if r else None
