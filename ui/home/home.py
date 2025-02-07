from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import sys

class Ui_HomeWindow(QMainWindow):

    def __init__(self):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        self.setAndRun()

    def setAndRun(self):
        self.tbSetting.setTabText(0, "Youtube")
        self.tbSetting.setTabText(1, "Douyin")

        self.btnDouyinDownload.clicked.connect(self.onBtnDouyinDownloadClick)
        

        self.show()

    def onBtnDouyinDownloadClick(self):
        url = self.tbUrlDouyinDownload.text()
        print("Download...")

        
    
    