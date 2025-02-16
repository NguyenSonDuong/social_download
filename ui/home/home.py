from PyQt5.QtWidgets import  QMainWindow, QGraphicsDropShadowEffect
from PyQt5 import uic
from youtube.youtube import  Youtube, YoutubeStatus
from PyQt5.QtGui import QColor, QPainter, QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt, QPoint,QEvent
from PyQt5.QtWidgets import QButtonGroup ,QFrame, QVBoxLayout,QLabel,QApplication,QCalendarWidget,QPushButton,QFileDialog
from douyin.douyin_key import Option as opDouyin
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta
import re
class WorkerThread(QThread):
    # Tạo 4 tín hiệu tương ứng với 4 hàm cần truyền
    processInfo = pyqtSignal(int, int)
    processDownload = pyqtSignal(list, list, int)
    processDownloadVideo = pyqtSignal(float, float, float, float, int)
    processError = pyqtSignal(str, int)

    def __init__(self,  url,count, order, from_date, to_date, download_folder):
        super().__init__()
        self.url = url
        self.count=count 
        self.order = order 
        self.from_date = from_date
        self.to_date=to_date 
        self.download_folder = download_folder

    def run(self):
        """Hàm chạy trong thread"""
        # Tạo đối tượng VideoProcessor và truyền các tín hiệu xuống lớp
        youtube = Youtube(
            self.processInfo.emit,  
            self.processDownload.emit,  
            self.processError.emit , 
            self.processDownloadVideo.emit
        )
        youtube.run(self.url,self.count, self.order, self.from_date, self.to_date, self.download_folder)

class QuantityVideoChannel(QThread):
    # Tạo 4 tín hiệu tương ứng với 4 hàm cần truyền
    processInfo = pyqtSignal(int)

    def __init__(self,  url):
        super().__init__()
        self.url = url

    def run(self):
        """Hàm chạy trong thread"""
        # Tạo đối tượng VideoProcessor và truyền các tín hiệu xuống lớp
        youtube = Youtube(
            self.processInfo.emit,
            None,
            None,
            None
        )
        self.processInfo.emit(youtube.getTotalVideoChannel(self.url))


class LoadingOverlay(QFrame):
    def __init__(self, parent=None, gif_path="loading.gif"):
        super().__init__(parent)
        self.resize(parent.size())
        self.setUIUX()

    def setUIUX(self):
        

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        

        # Tạo layout chính
        self.main_layout = QVBoxLayout(self)

        # Frame trung tâm
        self.frame = QFrame(self)
        uic.loadUi("ui/home/download.ui",self.frame)
        self.frame.btnClose.clicked.connect(self.hide_overlay)
        self.frame.setStyleSheet("background-color: white; border-radius: 10px;")
        self.frame.setFixedSize(650, 490)

        # Nội dung trong frame
        layout = QVBoxLayout(self.frame)
        # Đặt Frame vào giữa Overlay
        
        self.main_layout.addWidget(self.frame, alignment=Qt.AlignCenter)
    def setOverlayGeometry(self, target_widget):
        """Định vị overlay trùng với vùng sidebar"""
        self.setGeometry(target_widget.geometry())  
        # self.loading_label.move(self.width() // 2 - 25, self.height() // 2 - 25)  # Căn giữa GIF
    def paintEvent(self, event):
        """ Vẽ nền mờ """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
    def show_overlay(self):
        self.setVisible(True)  # Hiện overlay

    def hide_overlay(self):
        self.setVisible(False)  # Ẩn overlay

class Ui_HomeWindow(QMainWindow):
    
    _isClick = None
    
    def __init__(self, onYoutubeDownload, onDouyinDownload):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_active = False
        self._drag_position = QPoint()
        self.resize(1450, 865) 
        self.onYoutubeDownload = onYoutubeDownload
        self.onDouyinDownload = onDouyinDownload
        self.overlay = LoadingOverlay(self, "loading.gif")
        self.setAndRun()
        self.threadYoutube = None
        self.overlay.setOverlayGeometry(self.mainLayout) 
        self.overlay.hide_overlay()

    def processInfo(self, numberVideo, status):
        print(f"Đã lấy được: {numberVideo} - {status}")
    def processDownload(self, videoDownload, videoError,status):
        if status == YoutubeStatus.PROCESS:
            self.overlay.frame.pnAllsBar.setMaximum(int(self.txtQuatityDownload.text()))
            self.overlay.frame.pnAllsBar.setValue(len(videoDownload)+len(videoError))
            print(f"Đã tải được: {len(videoDownload)} - Video tải lỗi: {len(videoError)} - {status}")
        if status == YoutubeStatus.DONE:
            self.overlay.hide_overlay()
        if status == YoutubeStatus.ERROR:
            cursor = self.overlay.frame.txtLog.textCursor()
            red_format = QTextCharFormat()
            red_format.setForeground(QColor("red"))
            cursor.insertText(f"Lỗi: {videoError[0]["video_url"]} - {videoError[0]["title"]}\n", red_format)
    def processDownloadVideo(self,percent,speed,downloaded,total,status):
        if status == YoutubeStatus.PROCESS:
            self.overlay.frame.pnChildensBar.setMaximum(100)
            self.overlay.frame.pnChildensBar.setValue(int(percent))
        # if status == YoutubeStatus.DONE:
        #     self.overlay.hide_overlay()
        # self.pbDownload.setValue(int(percent))
    def processError(self, error, status):
        print(error)


    def startTask(self, url,count, order, from_date, to_date, download_folder):
        """Khởi chạy tiến trình"""
        if self.threadYoutube  and self.threadYoutube.isRunning():
            self.threadYoutube.wait()
            self.threadYoutube.typeRun = 1
        self.threadYoutube = WorkerThread(url,count, order, from_date, to_date, download_folder)

        # Kết nối tín hiệu từ Thread đến các hàm giao diện
        self.threadYoutube.processInfo.connect(self.processInfo)
        self.threadYoutube.processDownload.connect(self.processDownload)
        self.threadYoutube.processDownloadVideo.connect(self.processDownloadVideo)
        self.threadYoutube.processError.connect(self.processError)

        self.threadYoutube.start()

    def onBtnRunClick(self,event):
        
        url = self.txtUrl.text()
        if not url or not self.is_valid_url(url):
            print("Nhập đường dẫn đi")
            return
        quantity = int(self.txtQuatityDownload.text())
        

        from_date = datetime(1990,1,1)
        to_date = datetime.now()
        if self.rdDownloadDate.isChecked():
            from_date = datetime.now()
        elif self.rdDownloadWeek.isChecked():
            from_date = datetime.now() - timedelta(days=7)
        elif self.rdCustomTime.isChecked():
            from_date = datetime.strptime(self.txtFromDate.text(),"%d/%m/%Y")
            to_date = datetime.strptime(self.txtToDate.text(),"%d/%m/%Y")

        order = "date"
        if self.rdDownloadNewVideo.isChecked():
            order = "date"
        elif self.edDownloadTrending.isChecked():
            order = "viewCount"

        folder_download = self.txtFolderSaveVideo.text()
        self.overlay.show_overlay()
        self.startTask(url,quantity,order,from_date,to_date,folder_download)

    def setupLayout(self):
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
        self.runLayout.setAlignment(Qt.AlignRight)
        self.editAudioSaveResetLayout.setAlignment(Qt.AlignRight)


        self.editLayout.setAlignment(Qt.AlignTop)
        self.folderSaveVideoLayout.setAlignment(Qt.AlignTop)
        self.menuLayout.setAlignment(Qt.AlignTop)

        self.frNatBar.mousePressEvent = self.mousePressEvent
        self.frNatBar.mouseMoveEvent = self.mouseMoveEvent
        self.frNatBar.mouseReleaseEvent = self.mouseReleaseEvent

        self.btnClose.clicked.connect(self.onBtnCloseClick)
        self.btnMinimize.clicked.connect(self.onBtnMinimizeClick)

        self.setMouseTracking(True)
    def setupCalendar(self):
        self.calendarFrom = QCalendarWidget(self)
        self.calendarTo = QCalendarWidget(self)
        self.calendarFrom.setWindowFlags(self.calendarFrom.windowFlags() | 
                                     Qt.Popup)
        self.calendarTo.setWindowFlags(self.calendarTo.windowFlags() | 
                                     Qt.Popup)
        self.calendarFrom.clicked.connect(self.setDateCalendarFrom)
        self.calendarTo.clicked.connect(self.setDateCalendarTo)
        
        self.calendarFrom.hide()  # Ẩn khi khởi động
        self.calendarTo.hide()  # Ẩn khi khởi động
        
        self.txtFromDate.installEventFilter(self)
        self.txtToDate.installEventFilter(self)
    def setupNavigator(self):
        self.btnDouyin.installEventFilter(self)
        self.btnYoutube.installEventFilter(self)
        self.btnFacebook.installEventFilter(self)
        self.btInstagram.installEventFilter(self)
        self.btnTwitter.installEventFilter(self)
        self.btnSnapChat.installEventFilter(self)
        self.btnQQLive.installEventFilter(self)
    def setupShadowsForTheme(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.scrollAreaMain.setGraphicsEffect(shadow)


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
    def setupGroupCheckbox(self):
        self.groupOrder = QButtonGroup(self)

        self.groupOrder.addButton(self.rdDownloadNewVideo,1)
        self.groupOrder.addButton(self.edDownloadTrending,2)
        self.groupOrder.addButton(self.rdDownloadOld,3)
        self.groupOrder.addButton(self.rdDownloadDate,4)
        self.groupOrder.addButton(self.rdDownloadWeek,5)

    def setAndRun(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(150, 50)


        self.setupLayout()
        self.setupCalendar()
        self.setupNavigator()
        self.setupShadowsForTheme()
        self.setupGroupCheckbox()
        

        self.btnRun.clicked.connect(self.onBtnRunClick)
        self.btnSelectFolder.clicked.connect(self.onBtnSelectFolderClick)
        self.rdDownloadAllVideo.toggled.connect(self.onDownloadAllChecked)
        
        
        self.show()





    def onRdTimeCustomChecked(self):
        self.txtFromDate.setEnabled(self.rdCustomTime.isChecked())
        self.txtToDate.setEnabled(self.rdCustomTime.isChecked())


    def onDownloadAllChecked(self):
        """Hàm xử lý sự kiện khi RadioButton thay đổi trạng thái"""
         # Hiện lớp phủ
        self.txtQuatityDownload.setEnabled(not self.rdDownloadAllVideo.isChecked())
        QApplication.processEvents() 
        radio_button = self.sender()  # Lấy RadioButton kích hoạt sự kiện
        url = self.txtUrl.text()
        if not url or not self.is_valid_url(url):
            print("Nhập đường dẫn đi")
            return
        self.getQuantityVideo = QuantityVideoChannel(url)
        self.getQuantityVideo.processInfo.connect(self.processGetQuantityVideoChannel)
        if radio_button.isChecked():  

            if self.getQuantityVideo and self.getQuantityVideo.isRunning():
                self.getQuantityVideo.wait()
                self.getQuantityVideo.typeRun = 2
            self.overlay.show_overlay() 
            self.getQuantityVideo.start()

    def onBtnSelectFolderClick(self,event):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục", "")
        
        if folder_path:  # Nếu người dùng chọn thư mục
            self.txtFolderSaveVideo.setText(f"{folder_path}")








    def setDateCalendarFrom(self, date):
        formatted_date = date.toString("dd/MM/yyyy")  # Định dạng ngày
        self.txtFromDate.setText(formatted_date)
        self.calendarFrom.hide()  # Ẩn Calendar sau khi chọn ngày
        
    def setDateCalendarTo(self, date):
        """Lấy ngày đã chọn và hiển thị vào LineEdit"""
        formatted_date = date.toString("dd/MM/yyyy")  # Định dạng ngày
        self.txtToDate.setText(formatted_date)
        self.calendarTo.hide()  # Ẩn Calendar sau khi chọn ngày

    def is_valid_url(self,test):
        pattern = re.compile(
            r'^(https?|ftp)://'  # Bắt đầu với http://, https:// hoặc ftp://
            r'([a-zA-Z0-9.-]+)\.?([a-zA-Z]{2,})'  # Tên miền
            r'(:\d+)?(/.*)?$',  # Cổng (nếu có) và đường dẫn
            re.IGNORECASE
        )
        return re.match(pattern, test) is not None

    

    def processGetQuantityVideoChannel(self,quantity):
        print
        self.txtQuatityDownload.setText(f"{quantity}")
        self.overlay.hide_overlay()

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
        
        if obj == self.txtFromDate and event.type() == QEvent.MouseButtonPress:
            if self.calendarFrom.isVisible():
                self.calendarFrom.hide()
            else:
                # Lấy vị trí của nút trên màn hình (global position)
                button_pos = self.txtFromDate.mapToGlobal(self.txtFromDate.rect().bottomLeft())

                # Đặt CalendarWidget bên cạnh nút
                self.calendarFrom.move(button_pos.x(), button_pos.y())

                # Hiện Calendar
                self.calendarFrom.show()
            return True 

        if obj == self.txtToDate and event.type() == QEvent.MouseButtonPress:
            if self.calendarTo.isVisible():
                self.calendarTo.hide()
            else:
                # Lấy vị trí của nút trên màn hình (global position)
                button_pos = self.txtToDate.mapToGlobal(self.txtToDate.rect().bottomLeft())

                # Đặt CalendarWidget bên cạnh nút
                self.calendarTo.move(button_pos.x(), button_pos.y())

                # Hiện Calendar
                self.calendarTo.show()
            return True 
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
    
    