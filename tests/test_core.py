import sys,sqlite3,tempfile,json,time
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.database.db import Database
from app.services.project_service import ProjectService
from app.services.excel_service import ExcelService
from app.services.scan_service import ScanService
from app.services.import_service import ImportService
from app.services.export_service import ExportService
from app.utils.normalizer import *
SAMPLE=Path(__file__).resolve().parent/'fixtures'/'sample_inventory.xlsx'
def stack(tmp_path):
 db=Database(tmp_path/'t.db'); ps=ProjectService(db); pid=ps.create('تست','2026-10-07'); ss=ScanService(db,ps); return db,ps,pid,ss
def test_sample_structure_and_detection(tmp_path):
 assert SAMPLE.exists(); assert 'موجودی' in ExcelService.sheets(SAMPLE); h=ExcelService.detect_header(SAMPLE,'موجودی'); df=ExcelService.read(SAMPLE,'موجودی',h); assert h==0; assert ExcelService.detect_label_column(df)=='محصول'; assert df.iloc[0]['محصول']=='GD02002967 - میرو'
def test_normalization():
 s=NormalizationSettings(prefix='GD'); assert normalize_label(' GD02002967 - میرو ',s)=='GD02002967'; assert canonical_label('02002967',s)=='GD02002967'; assert canonical_label('00200',NormalizationSettings(prefix=''))=='00200'
def test_scan_existing_prefix_mismatch_duplicate_and_persistence(tmp_path):
 db,ps,pid,ss=stack(tmp_path); h=ExcelService.detect_header(SAMPLE,'موجودی'); ExcelService.load_inventory(db,pid,SAMPLE,'موجودی',h,'محصول',ps.settings(pid)); assert ss.add(pid,'GD02002967')['status']=='موجود'; assert ss.add(pid,'02002967')['status']=='تکراری'; assert ss.add(pid,'ZZ999999')['status']=='مغایرت'; assert ps.get(pid)['name']=='تست'; assert ss.stats(pid)['found']==1
def test_bulk_and_export(tmp_path):
 db,ps,pid,ss=stack(tmp_path); h=0; ExcelService.load_inventory(db,pid,SAMPLE,'موجودی',h,'محصول',ps.settings(pid)); f=tmp_path/'bulk.xlsx'; pd.DataFrame({'لیبل':['02002967','GD02002885','','BAD!','02002967']}).to_excel(f,index=False); imp=ImportService(db,ss,ps); a=imp.commit(f,'Sheet1','لیبل',pid); assert a['total']==5 and a['empty']==1 and a['invalid']==1 and a['duplicates']==1; out=tmp_path/'out.xlsx'; ExportService(db,ps,ss).export(pid,out); assert out.exists(); assert set(pd.ExcelFile(out).sheet_names)=={'خلاصه','موجود','مغایرت','تکراری','شمارش‌نشده','تمام اسکن‌ها'}
def test_100k_file(tmp_path):
 f=tmp_path/'big.xlsx'; pd.DataFrame({'محصول':[f'GD{i:08d} - تست' for i in range(100000)],'وزن':['1']*100000}).to_excel(f,index=False); df=ExcelService.read(f,'Sheet1',0); assert len(df)==100000; assert ExcelService.detect_label_column(df)=='محصول'; assert canonical_label(df.iloc[0]['محصول'])=='GD00000000'
