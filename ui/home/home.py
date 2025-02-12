from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from youtube.youtube_key import  Option
from PyQt5.QtCore import Qt, QPoint,QEvent
from PyQt5.QtWidgets import QGraphicsBlurEffect
from douyin.douyin_key import Option as opDouyin
import sys

class Ui_HomeWindow(QMainWindow):

    def __init__(self, onYoutubeDownload, onDouyinDownload):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        self.setAndRun()
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_active = False
        self._drag_position = QPoint()
        self.resize(1425, 856) 

        self.onYoutubeDownload = onYoutubeDownload
        self.onDouyinDownload = onDouyinDownload

    def setAndRun(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.louMain.setAlignment(Qt.AlignTop)
        self.selectVideoH.setAlignment(Qt.AlignLeft)
        self.selectSortLayout1.setAlignment(Qt.AlignLeft)
        self.selectSortLayout2.setAlignment(Qt.AlignLeft)
        self.numberDownloadLayout.setAlignment(Qt.AlignLeft)
        self.selectFrame.setAlignment(Qt.AlignLeft)
        self.selectSpeet.setAlignment(Qt.AlignLeft)
        self.cutVideoLayout.setAlignment(Qt.AlignLeft)
        self.editLayout.setAlignment(Qt.AlignTop)
        self.folderSaveVideoLayout.setAlignment(Qt.AlignTop)

        self.frNatBar.mousePressEvent = self.mousePressEvent
        self.frNatBar.mouseMoveEvent = self.mouseMoveEvent
        self.frNatBar.mouseReleaseEvent = self.mouseReleaseEvent

        # self.tbSetting.setTabText(0, "Youtube")
        # self.tbSetting.setTabText(1, "Douyin")

        # self.btnDouyinDownload.clicked.connect(self.onBtnDouyinDownloadClick)
        

        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False



    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            self.adjustSizeToScreen()
        super().changeEvent(event)

    def moveEvent(self, event):
        self.adjustSizeToScreen()
        super().moveEvent(event)

    def adjustSizeToScreen(self):
        self.resize(1425, 856)  
    
    