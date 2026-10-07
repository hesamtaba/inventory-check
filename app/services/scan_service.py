from datetime import datetime
from app.utils.normalizer import normalize_label,canonical_label,is_valid_label
class ScanService:
 def __init__(self,db,projects): self.db=db; self.projects=projects
 def add(self,pid,value,source='بارکدخوان/ورود دستی'):
  s=self.projects.settings(pid); entered=normalize_label(value,s); canon=canonical_label(value,s); now=datetime.now().isoformat(sep=' ',timespec='seconds')
  if not is_valid_label(entered,s): status='کد نامعتبر'
  else:
   prev=self.db.one('SELECT COUNT(*) n FROM scans WHERE project_id=? AND normalized_label=? AND deleted=0',(pid,canon))['n']
   if prev: status='تکراری'
   else: status='موجود' if self.db.one('SELECT id FROM inventory WHERE project_id=? AND normalized_label=? LIMIT 1',(pid,canon)) else 'مغایرت'
  sid=self.db.execute('INSERT INTO scans(project_id,entered_label,normalized_label,status,scanned_at,source) VALUES(?,?,?,?,?,?)',(pid,entered,canon,status,now,source)); self.projects.touch(pid)
  item=self.db.one('SELECT * FROM inventory WHERE project_id=? AND normalized_label=? LIMIT 1',(pid,canon))
  times=self.db.query('SELECT scanned_at,status FROM scans WHERE project_id=? AND normalized_label=? AND deleted=0 ORDER BY id',(pid,canon))
  return {'id':sid,'entered':entered,'normalized':canon,'status':status,'item':item,'times':times}
 def delete(self,sid): self.db.execute('UPDATE scans SET deleted=1 WHERE id=?',(sid,))
 def update_notes(self,sid,notes): self.db.execute('UPDATE scans SET notes=? WHERE id=?',(notes,sid))
 def stats(self,pid):
  inv=self.db.one('SELECT COUNT(*) n FROM inventory WHERE project_id=?',(pid,))['n']; total=self.db.one('SELECT COUNT(*) n FROM scans WHERE project_id=? AND deleted=0',(pid,))['n']
  unique_found=self.db.one("SELECT COUNT(DISTINCT normalized_label) n FROM scans WHERE project_id=? AND deleted=0 AND normalized_label IN (SELECT normalized_label FROM inventory WHERE project_id=?)",(pid,pid))['n']
  mis=self.db.one("SELECT COUNT(*) n FROM scans WHERE project_id=? AND deleted=0 AND status='مغایرت'",(pid,))['n']; dup=self.db.one("SELECT COUNT(*) n FROM scans WHERE project_id=? AND deleted=0 AND status='تکراری'",(pid,))['n']
  return {'inventory':inv,'scans':total,'found':unique_found,'mismatch':mis,'duplicate':dup,'unscanned':max(inv-unique_found,0),'progress':(unique_found/inv*100 if inv else 0)}
