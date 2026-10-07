import json,sys,logging
from pathlib import Path
from PySide6.QtCore import Qt,QThread,QDate
from PySide6.QtGui import QFont,QCloseEvent
from PySide6.QtWidgets import *
from app.database.db import Database
from app.services.project_service import ProjectService
from app.services.excel_service import ExcelService
from app.services.scan_service import ScanService
from app.services.import_service import ImportService
from app.services.export_service import ExportService
from app.utils.normalizer import NormalizationSettings
from app.workers.tasks import FunctionWorker
class MainWindow(QMainWindow):
 def __init__(self):
  super().__init__(); self.db=Database(); self.projects=ProjectService(self.db); self.scans=ScanService(self.db,self.projects); self.imports=ImportService(self.db,self.scans,self.projects); self.exports=ExportService(self.db,self.projects,self.scans); self.pid=None; self.last_scan=None; self.threads=[]
  self.setWindowTitle('مغایرت‌گیری موجودی و لیبل'); self.resize(1280,800); self.setLayoutDirection(Qt.RightToLeft); self.build(); self.refresh_projects()
 def build(self):
  root=QWidget(); self.setCentralWidget(root); lay=QVBoxLayout(root)
  top=QHBoxLayout(); self.project_combo=QComboBox(); self.project_combo.currentIndexChanged.connect(self.open_selected); top.addWidget(QLabel('پروژه:')); top.addWidget(self.project_combo,1)
  for text,fn in [('پروژه جدید',self.new_project),('بارگذاری موجودی',self.load_inventory_dialog),('ورود گروهی',self.bulk_dialog),('خروجی Excel',self.export_dialog),('تنظیمات',self.settings_dialog),('حذف پروژه',self.delete_project)]: b=QPushButton(text); b.clicked.connect(fn); top.addWidget(b)
  lay.addLayout(top); self.path_label=QLabel('فایل موجودی: -'); lay.addWidget(self.path_label)
  self.cards={}; cards=QHBoxLayout()
  for key,title in [('inventory','کل موجودی'),('scans','کل اسکن‌ها'),('found','موجود'),('mismatch','مغایرت'),('duplicate','تکراری'),('unscanned','شمارش‌نشده'),('progress','پیشرفت')]:
   box=QGroupBox(title); v=QVBoxLayout(box); lab=QLabel('0'); lab.setAlignment(Qt.AlignCenter); lab.setFont(QFont('',18,QFont.Bold)); v.addWidget(lab); self.cards[key]=lab; cards.addWidget(box)
  lay.addLayout(cards)
  self.scan=QLineEdit(); self.scan.setPlaceholderText('شماره لیبل را اسکن یا وارد کنید و Enter بزنید'); self.scan.setMinimumHeight(55); self.scan.setFont(QFont('',18)); self.scan.returnPressed.connect(self.do_scan); lay.addWidget(self.scan)
  self.result=QLabel('آماده ثبت'); self.result.setAlignment(Qt.AlignCenter); self.result.setMinimumHeight(55); self.result.setFont(QFont('',20,QFont.Bold)); lay.addWidget(self.result)
  actions=QHBoxLayout(); undo=QPushButton('حذف آخرین اسکن'); undo.clicked.connect(self.undo_last); actions.addWidget(undo); self.detail=QLabel(''); self.detail.setWordWrap(True); actions.addWidget(self.detail,1); lay.addLayout(actions)
  self.tabs=QTabWidget(); lay.addWidget(self.tabs,1); self.tables={}
  for name in ['موجود','مغایرت','تکراری','شمارش‌نشده','تمام اسکن‌ها']:
   w=QWidget(); vl=QVBoxLayout(w); search=QLineEdit(); search.setPlaceholderText('جستجو...'); table=QTableWidget(); table.setSortingEnabled(True); table.setEditTriggers(QAbstractItemView.NoEditTriggers); search.textChanged.connect(lambda t,ta=table:self.filter_table(ta,t)); vl.addWidget(search); vl.addWidget(table); self.tabs.addTab(w,name); self.tables[name]=table
 def new_project(self):
  d=QDialog(self); d.setWindowTitle('پروژه جدید'); f=QFormLayout(d); name=QLineEdit(); date=QDateEdit(QDate.currentDate()); date.setCalendarPopup(True); f.addRow('نام پروژه',name); f.addRow('تاریخ',date); bb=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.accepted.connect(d.accept); bb.rejected.connect(d.reject); f.addRow(bb)
  if d.exec() and name.text().strip(): self.projects.create(name.text().strip(),date.date().toString('yyyy-MM-dd')); self.refresh_projects()
 def refresh_projects(self):
  cur=self.pid; self.project_combo.blockSignals(True); self.project_combo.clear()
  for p in self.projects.list(): self.project_combo.addItem(p['name'],p['id'])
  self.project_combo.blockSignals(False)
  if self.project_combo.count():
   idx=self.project_combo.findData(cur) if cur else 0; self.project_combo.setCurrentIndex(max(idx,0)); self.open_selected()
  else: self.pid=None; self.refresh_all()
 def open_selected(self,*_):
  self.pid=self.project_combo.currentData(); self.refresh_all(); self.scan.setFocus()
 def load_inventory_dialog(self):
  if not self.pid: return self.msg('ابتدا یک پروژه ایجاد کنید.')
  path,_=QFileDialog.getOpenFileName(self,'انتخاب فایل موجودی','','Excel (*.xlsx *.xls)');
  if not path:return
  try: sheets=ExcelService.sheets(path)
  except Exception as e:return self.error(e)
  sheet,ok=QInputDialog.getItem(self,'انتخاب شیت','شیت موجودی:',sheets,0,False)
  if not ok:return
  try:
   h=ExcelService.detect_header(path,sheet); prev,col=ExcelService.preview(path,sheet,h)
   dlg=QDialog(self); dlg.resize(950,450); dlg.setWindowTitle('تأیید ساختار موجودی'); v=QVBoxLayout(dlg); v.addWidget(QLabel(f'ردیف سرستون پیشنهادی: {h+1}'))
   combo=QComboBox(); combo.addItems([str(x) for x in prev.columns]); combo.setCurrentText(str(col)); v.addWidget(QLabel('ستون شماره لیبل:')); v.addWidget(combo); table=QTableWidget(); self.fill_df(table,prev); v.addWidget(table); bb=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject); v.addWidget(bb)
   if dlg.exec(): self.run_bg(lambda:ExcelService.load_inventory(self.db,self.pid,path,sheet,h,combo.currentText(),self.projects.settings(self.pid)),lambda n:(self.msg(f'{n} قلم موجودی ثبت شد.'),self.refresh_all()))
  except Exception as e:self.error(e)
 def do_scan(self):
  if not self.pid:return self.msg('پروژه‌ای باز نیست.')
  value=self.scan.text(); self.scan.clear()
  try:r=self.scans.add(self.pid,value); self.last_scan=r['id']; self.show_result(r); self.refresh_all()
  except Exception as e:self.error(e)
  self.scan.setFocus()
 def show_result(self,r):
  self.result.setText(f"{r['status']} — {r['normalized']}"); colors={'موجود':'#d9ead3','مغایرت':'#f4cccc','تکراری':'#fce5cd','کد نامعتبر':'#f4cccc'}; self.result.setStyleSheet(f"background:{colors.get(r['status'],'white')};padding:10px;border-radius:6px")
  QApplication.beep()
  if r['item']:
   d=json.loads(r['item']['row_json']); self.detail.setText(' | '.join(f'{k}: {v}' for k,v in d.items() if v)[:1200])
  elif r['status']=='تکراری': self.detail.setText('زمان‌های ثبت: '+', '.join(x['scanned_at'] for x in r['times']))
  else:self.detail.setText('')
 def undo_last(self):
  if self.last_scan and QMessageBox.question(self,'تأیید','آخرین اسکن حذف شود؟')==QMessageBox.Yes:self.scans.delete(self.last_scan); self.last_scan=None; self.refresh_all()
 def bulk_dialog(self):
  if not self.pid:return self.msg('ابتدا پروژه را باز کنید.')
  path,_=QFileDialog.getOpenFileName(self,'فایل لیبل‌ها','','Excel (*.xlsx *.xls)');
  if not path:return
  try:
   sheets=ExcelService.sheets(path); sheet,ok=QInputDialog.getItem(self,'شیت','شیت:',sheets,0,False)
   if not ok:return
   df=ExcelService.read(path,sheet,ExcelService.detect_header(path,sheet)); col,ok=QInputDialog.getItem(self,'ستون','ستون شماره لیبل:',[str(x) for x in df.columns],0,False)
   if not ok:return
   a=self.imports.analyze(path,sheet,col,self.pid); text=f"کل: {a['total']} | معتبر: {a['valid']} | خالی: {a['empty']} | نامعتبر: {a['invalid']} | تکراری داخل فایل: {a['duplicates']}"
   if QMessageBox.question(self,'پیش‌نمایش ورود گروهی',text+'\n\nثبت انجام شود؟')==QMessageBox.Yes:self.run_bg(lambda:self.imports.commit(path,sheet,col,self.pid),lambda _:(self.msg('ورود گروهی انجام شد.'),self.refresh_all()))
  except Exception as e:self.error(e)
 def settings_dialog(self):
  if not self.pid:return
  s=self.projects.settings(self.pid); d=QDialog(self); f=QFormLayout(d); prefix=QLineEdit(s.prefix); split=QCheckBox(); split.setChecked(s.split_dash); upper=QCheckBox(); upper.setChecked(s.uppercase); minl=QSpinBox(); minl.setRange(1,100); minl.setValue(s.min_length); pat=QLineEdit(s.pattern); f.addRow('پیشوند',prefix); f.addRow('حذف متن بعد از خط تیره',split); f.addRow('حروف بزرگ انگلیسی',upper); f.addRow('حداقل طول',minl); f.addRow('الگوی Regex',pat); bb=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); bb.accepted.connect(d.accept); bb.rejected.connect(d.reject); f.addRow(bb)
  if d.exec(): self.projects.set_settings(self.pid,NormalizationSettings(upper.isChecked(),split.isChecked(),prefix.text().strip(),minl.value(),pat.text().strip())); self.msg('تنظیمات ذخیره شد.')
 def export_dialog(self):
  if not self.pid:return
  path,_=QFileDialog.getSaveFileName(self,'ذخیره گزارش','گزارش مغایرت.xlsx','Excel (*.xlsx)');
  if path:
   if not path.lower().endswith('.xlsx'):path+='.xlsx'
   self.run_bg(lambda:self.exports.export(self.pid,path),lambda p:self.msg(f'گزارش ذخیره شد:\n{p}'))
 def delete_project(self):
  if self.pid and QMessageBox.warning(self,'حذف پروژه','پروژه و همه اسکن‌های آن حذف شود؟',QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:self.projects.delete(self.pid); self.pid=None; self.refresh_projects()
 def refresh_all(self):
  p=self.projects.get(self.pid) if self.pid else None; self.path_label.setText('فایل موجودی: '+(p['inventory_path'] if p and p['inventory_path'] else '-'))
  if not self.pid:
   for x in self.cards.values():x.setText('0')
   return
  st=self.scans.stats(self.pid)
  for k,v in st.items(): self.cards[k].setText(f'{v:.1f}%' if k=='progress' else str(v))
  scans=self.db.query('SELECT * FROM scans WHERE project_id=? AND deleted=0 ORDER BY id DESC',(self.pid,)); inv=self.db.query('SELECT * FROM inventory WHERE project_id=? ORDER BY row_no',(self.pid,)); found={x['normalized_label'] for x in scans if x['status'] in ('موجود','تکراری')}
  mapping={'موجود':[x for x in scans if x['status']=='موجود'],'مغایرت':[x for x in scans if x['status'] in ('مغایرت','کد نامعتبر')],'تکراری':[x for x in scans if x['status']=='تکراری'],'تمام اسکن‌ها':scans}
  for n,rows in mapping.items():self.fill_rows(self.tables[n],rows,['id','entered_label','normalized_label','status','scanned_at','source','notes'])
  self.fill_rows(self.tables['شمارش‌نشده'],[x for x in inv if x['normalized_label'] not in found],['row_no','original_label','normalized_label'])
 def fill_rows(self,t,rows,cols):
  t.setSortingEnabled(False); t.clear(); t.setColumnCount(len(cols)); t.setHorizontalHeaderLabels(cols); t.setRowCount(len(rows))
  for i,r in enumerate(rows):
   for j,c in enumerate(cols):t.setItem(i,j,QTableWidgetItem(str(r.get(c,''))))
  t.resizeColumnsToContents(); t.setSortingEnabled(True)
 def fill_df(self,t,df):
  t.setRowCount(len(df)); t.setColumnCount(len(df.columns)); t.setHorizontalHeaderLabels([str(x) for x in df.columns])
  for i,row in df.iterrows():
   for j,v in enumerate(row):t.setItem(i,j,QTableWidgetItem(str(v)))
  t.resizeColumnsToContents()
 def filter_table(self,t,text):
  q=text.lower()
  for r in range(t.rowCount()):t.setRowHidden(r,not any(q in (t.item(r,c).text().lower() if t.item(r,c) else '') for c in range(t.columnCount())))
 def run_bg(self,fn,done):
  th=QThread(self); w=FunctionWorker(fn); w.moveToThread(th); th.started.connect(w.run); w.finished.connect(done); w.finished.connect(th.quit); w.error.connect(self.error); w.error.connect(th.quit); th.finished.connect(lambda:self.threads.remove(th) if th in self.threads else None); self.threads.append(th); th.start()
 def msg(self,x):QMessageBox.information(self,'InventoryChecker',str(x))
 def error(self,e):logging.exception('UI error: %s',e); QMessageBox.critical(self,'خطا','عملیات انجام نشد. لطفاً فایل و تنظیمات را بررسی کنید.\n'+str(e))
 def closeEvent(self,e:QCloseEvent):
  if QMessageBox.question(self,'خروج','از برنامه خارج می‌شوید؟')==QMessageBox.Yes:e.accept()
  else:e.ignore()
