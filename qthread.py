import sys, time
from PyQt4 import QtGui as qt
from PyQt4 import QtCore as qtcore

app = qt.QApplication(sys.argv)
class widget(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self)

    def appinit(self):
        thread = worker()
        self.connect(thread, thread.signal, self.testfunc)
        thread.start()

    def testfunc(self, sigstr):
        print sigstr

class worker(qtcore.QThread):
    def __init__(self):
        qtcore.QThread.__init__(self, parent=app)
        self.signal = qtcore.SIGNAL("signal")
    def run(self):
        #time.sleep(5)
        print "in thread"
        self.emit(self.signal, "hi from thread")

def main():
    w = widget()
    w.show()
    qtcore.QTimer.singleShot(0, w.appinit)
    sys.exit(app.exec_())

main()