from datetime import datetime
import json
from app.utils.normalizer import NormalizationSettings
class ProjectService:
 def __init__(self,db): self.db=db
 def create(self,name,date=''):
  now=datetime.now().isoformat(timespec='seconds'); return self.db.execute('INSERT INTO projects(name,project_date,created_at,updated_at,normalization_json) VALUES(?,?,?,?,?)',(name,date,now,now,json.dumps(NormalizationSettings().__dict__,ensure_ascii=False)))
 def list(self,include_archived=False): return self.db.query('SELECT * FROM projects '+('' if include_archived else 'WHERE archived=0 ')+'ORDER BY updated_at DESC')
 def get(self,pid): return self.db.one('SELECT * FROM projects WHERE id=?',(pid,))
 def touch(self,pid): self.db.execute('UPDATE projects SET updated_at=? WHERE id=?',(datetime.now().isoformat(timespec='seconds'),pid))
 def archive(self,pid): self.db.execute('UPDATE projects SET archived=1 WHERE id=?',(pid,))
 def delete(self,pid): self.db.execute('DELETE FROM projects WHERE id=?',(pid,))
 def settings(self,pid):
  p=self.get(pid); d=json.loads(p['normalization_json'] or '{}'); return NormalizationSettings(**{**NormalizationSettings().__dict__,**d})
 def set_settings(self,pid,s): self.db.execute('UPDATE projects SET normalization_json=?,updated_at=? WHERE id=?',(json.dumps(s.__dict__,ensure_ascii=False),datetime.now().isoformat(timespec='seconds'),pid))
