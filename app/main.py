import sys,logging
from PySide6.QtWidgets import QApplication
from app.config import LOG_DIR,resource_path
from app.ui.main_window import MainWindow
def main():
 logging.basicConfig(filename=LOG_DIR/'app.log',level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',encoding='utf-8')
 app=QApplication(sys.argv); app.setApplicationName('InventoryChecker'); app.setLayoutDirection(__import__('PySide6.QtCore',fromlist=['Qt']).Qt.RightToLeft)
 qss=resource_path('assets/styles.qss')
 if qss.exists():app.setStyleSheet(qss.read_text(encoding='utf-8'))
 w=MainWindow(); w.show(); sys.exit(app.exec())
if __name__=='__main__':main()
