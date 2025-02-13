from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PyQt5 import uic
from youtube.youtube_key import  Option
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QSize,QEvent
from PyQt5.QtWidgets import QGraphicsBlurEffect
from douyin.douyin_key import Option as opDouyin
import sys

class Ui_HomeWindow(QMainWindow):
    
    _isClick = None
    def __init__(self, onYoutubeDownload, onDouyinDownload):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        self.setAndRun()
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_active = False
        self._drag_position = QPoint()
        self.resize(1450, 865) 
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
        self.editColorBasicLayout.setAlignment(Qt.AlignLeft)
        self.editColorAdvancedLayout.setAlignment(Qt.AlignLeft)
        self.volumMainLayout.setAlignment(Qt.AlignLeft)
        self.upVolumLayout.setAlignment(Qt.AlignLeft)
        self.editVolumeSizeLayout.setAlignment(Qt.AlignLeft)
        self.bigToSmallVolume.setAlignment(Qt.AlignLeft)
        self.smallToBigVolumeLayout.setAlignment(Qt.AlignLeft)


        self.editVideoSaveResetLayout.setAlignment(Qt.AlignRight)
        self.editColorSaveResetLayout.setAlignment(Qt.AlignRight)
        self.editAudioSaveResetLayout.setAlignment(Qt.AlignRight)



        self.editLayout.setAlignment(Qt.AlignTop)
        self.folderSaveVideoLayout.setAlignment(Qt.AlignTop)
        self.menuLayout.setAlignment(Qt.AlignTop)

        self.frNatBar.mousePressEvent = self.mousePressEvent
        self.frNatBar.mouseMoveEvent = self.mouseMoveEvent
        self.frNatBar.mouseReleaseEvent = self.mouseReleaseEvent
        self.setMouseTracking(True)

        

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.scrollAreaMain.setGraphicsEffect(shadow)

        
        self.btnDouyin.installEventFilter(self)
        self.btnYoutube.installEventFilter(self)
        self.btnFacebook.installEventFilter(self)
        self.btInstagram.installEventFilter(self)
        self.btnTwitter.installEventFilter(self)
        self.btnSnapChat.installEventFilter(self)
        self.btnQQLive.installEventFilter(self)

        self.btnClose.clicked.connect(self.onBtnCloseClick)
        self.btnMinimize.clicked.connect(self.onBtnMinimizeClick)

        shadow3 = QGraphicsDropShadowEffect(self)
        shadow3.setBlurRadius(30)
        shadow3.setOffset(2, 2)
        shadow3.setColor(QColor(0, 0, 0, 80)) 
        self.editLayout_3.setGraphicsEffect(shadow3)



        shadow4 = QGraphicsDropShadowEffect(self)
        shadow4.setBlurRadius(30)
        shadow4.setOffset(2, 2)
        shadow4.setColor(QColor(0, 0, 0, 80)) 
        self.editColorLayout.setGraphicsEffect(shadow4)


        shadow5 = QGraphicsDropShadowEffect(self)
        shadow5.setBlurRadius(30)
        shadow5.setOffset(2, 2)
        shadow5.setColor(QColor(0, 0, 0, 80)) 
        self.editAudioLayout.setGraphicsEffect(shadow5)
        
        self.setMinimumSize(150, 50)
        self.show()


    def onBtnCloseClick(self,event):
        self.close()

    
    def onBtnMinimizeClick(self,event):
        self.showMinimized()  

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:  # Khi di chuột vào
            if self._isClick != obj:
                shadow = QGraphicsDropShadowEffect(obj)
                shadow.setBlurRadius(15)  
                shadow.setOffset(3, 3)  
                shadow.setColor(QColor(0, 0, 0, 100)) 
                obj.setGraphicsEffect(shadow)  
        elif event.type() == QEvent.Leave: 
            if self._isClick != obj:
                obj.setGraphicsEffect(None)
        elif event.type() == QEvent.MouseButtonPress:
            if self._isClick != obj:
                if self._isClick != None:
                    self._isClick.setGraphicsEffect(None) 
                shadow = QGraphicsDropShadowEffect(obj)
                shadow.setBlurRadius(15)  
                shadow.setOffset(3, 3)  
                shadow.setColor(QColor(0, 0, 0, 100)) 
                obj.setGraphicsEffect(shadow)  
                self._isClick = obj
        return super().eventFilter(obj, event)




    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos()  
            event.accept()  

    def mouseMoveEvent(self, event):
        if self.start_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.start_pos
            self.window().move(self.window().pos() + delta)
            self.start_pos = event.globalPos()
            event.accept()  

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        event.accept()  

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            self.adjustSizeToScreen()
        super().changeEvent(event)

    def moveEvent(self, event):
        self.adjustSizeToScreen()
        super().moveEvent(event)

    def adjustSizeToScreen(self):
        self.resize(1450, 865)  
    
    