import pandas as pd
from datetime import datetime
from app.utils.normalizer import normalize_label,is_valid_label,canonical_label
class ImportService:
 def __init__(self,db,scan,projects): self.db=db; self.scan=scan; self.projects=projects
 def analyze(self,path,sheet,column,pid):
  df=pd.read_excel(path,sheet_name=sheet,dtype=str,keep_default_na=False,engine='openpyxl' if str(path).lower().endswith('xlsx') else None); s=self.projects.settings(pid); vals=[normalize_label(x,s) for x in df[column].tolist()]
  valid=[v for v in vals if is_valid_label(v,s)]; can=[canonical_label(v,s) for v in valid]
  return {'total':len(vals),'valid':len(valid),'empty':sum(not v for v in vals),'invalid':sum(bool(v) and not is_valid_label(v,s) for v in vals),'duplicates':len(can)-len(set(can)),'values':valid,'preview':df.head(10)}
 def commit(self,path,sheet,column,pid):
  a=self.analyze(path,sheet,column,pid)
  for v in a['values']: self.scan.add(pid,v,'ورود گروهی')
  self.db.execute('INSERT INTO imports(project_id,file_path,sheet_name,column_name,imported_at,total_rows,valid_rows,empty_rows,invalid_rows,duplicate_rows) VALUES(?,?,?,?,?,?,?,?,?,?)',(pid,str(path),sheet,str(column),datetime.now().isoformat(sep=' ',timespec='seconds'),a['total'],a['valid'],a['empty'],a['invalid'],a['duplicates']))
  return a
