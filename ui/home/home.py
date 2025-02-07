from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from youtube.youtube_key import  Option
import sys

class Ui_HomeWindow(QMainWindow):

    def __init__(self, onYoutubeDownload, onDouyinDownload):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        self.setAndRun()
        self.onYoutubeDownload = onYoutubeDownload
        self.onDouyinDownload = onDouyinDownload

    def setAndRun(self):
        self.tbSetting.setTabText(0, "Youtube")
        self.tbSetting.setTabText(1, "Douyin")

        self.btnDouyinDownload.clicked.connect(self.onBtnDouyinDownloadClick)
        

        self.show()

    def onBtnDouyinDownloadClick(self):
        url = self.tbUrlDouyinDownload.text()
        option = Option()
        option.channel_url = url
        self.onDouyinDownload(option)
        print("Download...")

        
    
    