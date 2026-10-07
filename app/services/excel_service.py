from pathlib import Path
import pandas as pd
from app.utils.normalizer import normalize_label,canonical_label
CANDIDATES=['لیبل','شماره لیبل','کد','کد کالا','محصول','barcode','item code']
class ExcelService:
 @staticmethod
 def sheets(path): return pd.ExcelFile(path).sheet_names
 @staticmethod
 def detect_header(path,sheet):
  raw=pd.read_excel(path,sheet_name=sheet,header=None,nrows=30,dtype=str,engine='openpyxl' if str(path).lower().endswith('xlsx') else None)
  best=(0,-1)
  for i,row in raw.iterrows():
   vals=[str(x).strip().lower() for x in row.dropna().tolist()]
   score=sum(any(c in v for c in CANDIDATES) for v in vals)+len(vals)*.01
   if score>best[1]: best=(i,score)
  return best[0]
 @staticmethod
 def read(path,sheet,header_row): return pd.read_excel(path,sheet_name=sheet,header=header_row,dtype=str,keep_default_na=False,engine='openpyxl' if str(path).lower().endswith('xlsx') else None)
 @staticmethod
 def detect_label_column(df):
  cols=list(df.columns); lower={c:str(c).strip().lower() for c in cols}
  for cand in CANDIDATES:
   for c in cols:
    if lower[c]==cand: return c
  for cand in CANDIDATES:
   for c in cols:
    if cand in lower[c]: return c
  # content heuristic: prefer columns containing GD-like identifiers
  scores={c:sum(bool(__import__('re').match(r'^\s*[A-Za-z]{1,5}\d{4,}',str(v))) for v in df[c].head(100)) for c in cols}
  return max(scores,key=scores.get)
 @staticmethod
 def preview(path,sheet,header_row):
  df=ExcelService.read(path,sheet,header_row); return df.head(10),ExcelService.detect_label_column(df)
 @staticmethod
 def load_inventory(db,pid,path,sheet,header_row,label_col,settings):
  df=ExcelService.read(path,sheet,header_row); records=[]
  for idx,row in df.iterrows():
   orig=str(row.get(label_col,'')).strip(); norm=canonical_label(orig,settings)
   if not norm: continue
   data={str(k):('' if pd.isna(v) else str(v)) for k,v in row.items()}
   records.append((pid,int(idx)+header_row+2,orig,norm,__import__('json').dumps(data,ensure_ascii=False)))
  with db.conn() as c:
   c.execute('DELETE FROM inventory WHERE project_id=?',(pid,)); c.executemany('INSERT INTO inventory(project_id,row_no,original_label,normalized_label,row_json) VALUES(?,?,?,?,?)',records)
   c.execute('UPDATE projects SET inventory_path=?,inventory_sheet=?,label_column=?,header_row=?,updated_at=datetime("now","localtime") WHERE id=?',(str(Path(path)),sheet,str(label_col),header_row+1,pid))
  return len(records)
