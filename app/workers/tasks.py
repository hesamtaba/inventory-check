from PySide6.QtCore import QObject,Signal,Slot
class FunctionWorker(QObject):
 finished=Signal(object); error=Signal(str)
 def __init__(self,fn,*a,**kw): super().__init__(); self.fn=fn; self.a=a; self.kw=kw
 @Slot()
 def run(self):
  try:self.finished.emit(self.fn(*self.a,**self.kw))
  except Exception as e:self.error.emit(str(e))
