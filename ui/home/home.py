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
import os
import json


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
    processError = pyqtSignal(str, int)
    def __init__(self,  url):
        super().__init__()
        self.url = url

    def run(self):
        """Hàm chạy trong thread"""
        # Tạo đối tượng VideoProcessor và truyền các tín hiệu xuống lớp
        youtube = Youtube(
            self.processInfo.emit,
            None,
            self.processError.emit,
            None
        )
        self.processInfo.emit(youtube.getTotalVideoChannel(self.url))


class LoadingOverlay(QFrame):
    def __init__(self, parent=None, gif_path="loading.gif"):
        super().__init__(parent)
        self.resize(parent.size())
        self.threadYoutube = None
        self.setUIUX()

    def setUIUX(self):

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.main_layout = QVBoxLayout(self)
        self.frame = QFrame(self)
        uic.loadUi("ui/home/download.ui",self.frame)
        self.frame.btnClose.clicked.connect(self.hide_overlay)
        self.frame.setStyleSheet("background-color: white; border-radius: 10px;")
        self.frame.setFixedSize(650, 490)
        layout = QVBoxLayout(self.frame)
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

    setting = {
        "type_download":"0",
        "order_download":"0",
        "from_time": "",
        "to_time":"",
        "folder_save_video":"",
        "edit_video":{
            "frame":"0",
            "speed_video":"0",
            "speed_video_custom":"0",
            "cut_video":"0",
            "cut_video_custom":{
                "start":"0",
                "end":"0"
            },
            "save_folder_edit_video":"",
            "intro_video":"",
            "outro_video":"",
            "left_video":"",
            "right_video":"",
            "top_video":"",
            "bottom_video":"",
        },
        "color":{
            "opacity":"",
            "red":"",
            "green":"",
            "blue":"",
            "birghtness":"",
            "color_custom":"",
            "saturation":"",
            "gamma":"",
            "hue":"",
            "audio_tone":""
        },
        "audio":{
            "main_volum":"0",
            "audio_tone":"0",
            "volum_all":"0",
            "mix_audio":"",
            "edit_audio":"0",
            "fade_in":"0",
            "fade_out":"0"
        }
    }

    _isClick = None
    def __init__(self):
        sys.path.append('.')
        super().__init__()
        uic.loadUi("ui/home/home.ui",self)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self._drag_active = False
        self._drag_position = QPoint()
        self.resize(1450, 865) 
        self.overlay = LoadingOverlay(self, "loading.gif")
        self.setAndRun()
        self.threadYoutube = None
        
        self.overlay.setOverlayGeometry(self.mainLayout) 
        self.overlay.hide_overlay()

    def setupEditColorSetting(self):
        self.txtOpacity.setText(self.setting["color"]["opacity"])
        self.txtRed.setText(self.setting["color"]["red"])
        self.txtGreen.setText(self.setting["color"]["green"])
        self.txtBlue.setText(self.setting["color"]["blue"])
        self.txtBrightness.setText(self.setting["color"]["birghtness"])
        self.txtColorCustom.setText(self.setting["color"]["color_custom"])
        self.txtSatuation.setText(self.setting["color"]["saturation"])
        self.txtGamma.setText(self.setting["color"]["gamma"])
        self.txtHue.setText(self.setting["color"]["hue"])
        self.txtAudioTone.setText(self.setting["color"]["audio_tone"])
        
    def setupEditVideoSetting(self):
        if self.setting["edit_video"]["frame"] == "1":
            self.rd169.setChecked(True)
        if self.setting["edit_video"]["frame"] == "2":
            self.rd619.setChecked(True)
        if self.setting["edit_video"]["frame"] == "3":
            self.rd43.setChecked(True)

        if self.setting["edit_video"]["speed_video"] == "1":
            self.rdSpeedKeep.setChecked(True)
        if self.setting["edit_video"]["speed_video"] == "2":
            self.rdSpeedx2.setChecked(True)
        if self.setting["edit_video"]["speed_video"] == "3":
            self.rdSpeedx4.setChecked(True)
        self.txtSppedCustom.setText(self.setting["edit_video"]["speed_video_custom"])

        if self.setting["edit_video"]["cut_video"] == "1":
            self.rdCut3sStart.setChecked(True)
        if self.setting["edit_video"]["cut_video"] == "2":
            self.rdCutSpped3sEnd.setChecked(True)
        if self.setting["edit_video"]["cut_video"] == "3":
            self.rdCut1sForeach5s.setChecked(True)
        
        
        self.txtCutStart.setText(self.setting["edit_video"]["cut_video_custom"]["start"])
        self.txtCutEnd.setText(self.setting["edit_video"]["cut_video_custom"]["end"])

        self.txtFolderSave.setText(self.setting["edit_video"]["save_folder_edit_video"])

        self.txtInto.setText(self.setting["edit_video"]["intro_video"])
        self.txtOutro.setText(self.setting["edit_video"]["outro_video"])
        self.txtRowVideoLeft.setText(self.setting["edit_video"]["left_video"])
        self.txtRowVideoRight.setText(self.setting["edit_video"]["right_video"])
        self.txtColumLeft.setText(self.setting["edit_video"]["top_video"])
        self.txtColumRight.setText(self.setting["edit_video"]["bottom_video"])

    def setupDownloadVideoSetting(self):
        if self.setting["type_download"] == "1":
            self.rdDownloadFromLink.setChecked(True)
        if self.setting["type_download"] == "2":
            self.rdFullChannel.setChecked(True)
        if self.setting["type_download"] == "3":
            self.rdFromKey.setChecked(True)

        if self.setting["order_download"] == "1":
            self.rdDownloadNewVideo.setChecked(True)
        if self.setting["order_download"] == "2":
            self.edDownloadTrending.setChecked(True)
        if self.setting["order_download"] == "3":
            self.rdDownloadOld.setChecked(True)

        if self.setting["order_download"] == "4":
            self.rdDownloadDate.setChecked(True)
        if self.setting["order_download"] == "5":
            self.rdDownloadWeek.setChecked(True)
        if self.setting["order_download"] == "6":
            self.rdCustomTime.setChecked(True)

        if self.setting["from_time"]:
            self.txtFromDate.setText(self.setting["from_time"])
        if self.setting["to_time"]:
            self.txtToDate.setText(self.setting["to_time"])

        if self.setting["folder_save_video"]:
            self.txtFolderSaveVideo.setText(self.setting["folder_save_video"])

    def setupEditAudioSetiing(self):
        self.txtMainVolum.setText(self.setting["audio"]["main_volum"])
        self.txtAudioTone.setText(self.setting["audio"]["audio_tone"])
        self.txtNumberVolum.setText(self.setting["audio"]["volum_all"])

        self.txtFolderMusicVideo.setText(self.setting["audio"]["mix_audio"])

        self.txtEditAudio.setText(self.setting["audio"]["edit_audio"])
        self.txtFadeIn.setText(self.setting["audio"]["fade_in"])
        self.txtFadeOut.setText(self.setting["audio"]["fade_out"])

    def setupdSetting(self):
        self.setupEditColorSetting()
        self.setupEditVideoSetting()
        self.setupDownloadVideoSetting()
        self.setupEditAudioSetiing()

    def saveDownloadSetting(self):
        self.setting["type_download"] = "1" if self.rdDownloadFromLink.isChecked() else "2" if self.rdFullChannel.isChecked() else "3"
        self.setting["order_download"] = "1" if self.rdDownloadNewVideo.isChecked() else "2" if self.edDownloadTrending.isChecked() else "3" if self.rdDownloadOld.isChecked() else "4" if self.rdDownloadDate.isChecked() else "5" if self.rdDownloadWeek.isChecked() else "6"
        self.setting["folder_save_video"] = self.txtFolderSaveVideo.text()

    def saveEditVideoSetting(self):
        self.setting["edit_video"]["frame"] = "1" if self.rd169.isChecked() else "2" if self.rd619.isChecked() else "3"
        self.setting["edit_video"]["speed_video"] = "1" if self.rdSpeedKeep.isChecked() else "2" if self.rdSpeedx2.isChecked() else "3" 
        self.setting["edit_video"]["cut_video"] = "1" if self.rdCut3sStart.isChecked() else "2" if self.rdCutSpped3sEnd.isChecked() else "3"
        self.setting["edit_video"]["cut_video_custom"]["start"] = self.txtCutStart.text()
        self.setting["edit_video"]["cut_video_custom"]["end"] = self.txtCutEnd.text()
        self.setting["edit_video"]["intro_video"] = self.txtInto.text()
        self.setting["edit_video"]["outro_video"] = self.txtOutro.text()
        self.setting["edit_video"]["left_video"] = self.txtRowVideoLeft.text()
        self.setting["edit_video"]["right_video"] = self.txtRowVideoRight.text()
        self.setting["edit_video"]["top_video"] = self.txtColumLeft.text()
        self.setting["edit_video"]["bottom_video"] = self.txtColumRight.text()

    def saveEditAudioSetting(self):
        self.setting["audio"]["main_volum"] = self.txtMainVolum.text()
        self.setting["audio"]["audio_tone"] = self.txtAudioTone.text()
        self.setting["audio"]["volum_all"] = self.txtNumberVolum.text()
        self.setting["audio"]["mix_audio"] = self.txtFolderMusicVideo.text()
        self.setting["audio"]["edit_audio"] = self.txtEditAudio.text()
        self.setting["audio"]["fade_in"] = self.txtFadeIn.text()
        self.setting["audio"]["fade_out"] = self.txtFadeOut.text()

    def saveEditColorSetting(self):
        self.setting["color"]["opacity"] = self.txtOpacity.text()
        self.setting["color"]["red"] = self.txtRed.text()
        self.setting["color"]["green"] = self.txtGreen.text()
        self.setting["color"]["blue"] = self.txtBlue.text()
        self.setting["color"]["birghtness"] = self.txtBrightness.text()
        self.setting["color"]["color_custom"] = self.txtColorCustom.text()
        self.setting["color"]["saturation"] = self.txtSatuation.text()
        self.setting["color"]["gamma"] = self.txtGamma.text()
        self.setting["color"]["hue"] = self.txtHue.text()
        self.setting["color"]["audio_tone"] = self.txtAudioTone_2.text()

    def is_folder(self,path):
        return os.path.isdir(path)

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
            self.log("Lỗi lấy thông số video! ")

    def processDownloadVideo(self,percent,speed,downloaded,total,status):
        if status == YoutubeStatus.PROCESS:
            self.overlay.frame.pnChildensBar.setMaximum(100)
            self.overlay.frame.pnChildensBar.setValue(int(percent))

    def processError(self, error, status):
        self.log(str(error))
        print(error)

    def log(self, text, color="red"):
        cursor = self.overlay.frame.txtLog.textCursor()
        red_format = QTextCharFormat()
        red_format.setForeground(QColor(color))
        cursor.insertText(f"{text}\n", red_format)

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
        self.overlay.threadYoutube = self.threadYoutube
        self.threadYoutube.start()

    def onBtnRunClick(self,event):

        if self.threadYoutube and self.threadYoutube.isRunning():
            self.overlay.show_overlay()
            return

        url = self.txtUrl.text()

        if not url or not self.is_valid_url(url):
            print("Nhập đường dẫn đi")
            self.lbErrorUrl.show()
            return
        
        self.lbErrorUrl.hide()

        if self.txtQuatityDownload.text():
            quantity = int(self.txtQuatityDownload.text())
        elif self.rdDownloadAllVideo.isChecked():
            quantity = -1
        else:
            self.lbErrorQuantity.show()
            return
        self.lbErrorQuantity.hide()

        if self.rdDownloadNewVideo.isChecked() or self.edDownloadTrending.isChecked() or self.rdDownloadOld.isChecked():
            from_date = None
            to_date = None
        else:    
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
        if self.rdDownloadOld.isChecked():
            order = "old"
        elif self.edDownloadTrending.isChecked():
            order = "viewCount"

        folder_download = self.txtFolderSaveVideo.text()
        if not folder_download or not self.is_folder(folder_download):
            self.lbErrorSelectFolder.show()
            return
        self.lbErrorSelectFolder.hide()

        self.overlay.show_overlay()

        self.startTask(url,quantity,order,from_date,to_date,folder_download)

    def setupLayout(self):
        self.louMain.setAlignment(Qt.AlignTop)

        self.selectVideoH.setAlignment(Qt.AlignLeft)
        self.selectSortLayout1.setAlignment(Qt.AlignLeft)
        self.selectSortLayout2.setAlignment(Qt.AlignLeft)
        self.numberDownloadLayout.setAlignment(Qt.AlignLeft)
        self.selectFrame.setAlignment(Qt.AlignLeft)
        self.selectSpeet_2.setAlignment(Qt.AlignLeft)
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
        self.groupOrder.addButton(self.rdCustomTime,6)

        self.groupFrame = QButtonGroup(self)
        self.groupFrame.addButton(self.rd169,1)
        self.groupFrame.addButton(self.rd619,2)
        self.groupFrame.addButton(self.rd43,3)

        self.groupSpeed = QButtonGroup(self)
        self.groupSpeed.addButton(self.rdSpeedKeep,1)
        self.groupSpeed.addButton(self.rdSpeedx2,2)
        self.groupSpeed.addButton(self.rdSpeedx4,3)

        self.groupCut = QButtonGroup(self)
        self.groupCut.addButton(self.rdCut3sStart,1)
        self.groupCut.addButton(self.rdCutSpped3sEnd,2)
        self.groupCut.addButton(self.rdCut1sForeach5s,3)



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

        self.btnSaveEditVideo.clicked.connect(self.onBtnSaveEditVideoClick)
        self.btnEditColorVideo.clicked.connect(self.onBtnEditColorVideoClick)
        self.btnSaveAudioSetting.clicked.connect(self.onBtnSaveAudioSettingClick)

        # self.rdDownloadAllVideo.toggled.connect(self.onDownloadAllChecked)
        
        
        self.lbErrorUrl.hide()
        self.lbErrorQuantity.hide()
        self.lbErrorSelectFolder.hide()
        self.loadSettingFromFile()
        self.setupdSetting()

        self.show()

    def onBtnSaveEditVideoClick(self):
        self.saveEditVideoSetting()
        self.saveSettingToFile()
    def onBtnEditColorVideoClick(self):
        self.saveEditColorSetting()
        self.saveSettingToFile()
    def onBtnSaveAudioSettingClick(self):
        self.saveEditAudioSetting()
        self.saveSettingToFile()

    def saveSettingToFile(self):
        jsonStr = json.dumps(self.setting)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        setting_path = os.path.join(current_dir, "..", "setting", "setting.json")
        with open(setting_path,"w", encoding="utf-8") as file:
            file.write(jsonStr)

    def loadSettingFromFile(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        setting_path = os.path.join(current_dir, "..", "setting", "setting.json")
        with open(setting_path,"r", encoding="utf-8") as file:
            str = file.read()
            try:
                self.setting = json.loads(str)
            except Exception as ex:
                return
    
    def onRdTimeCustomChecked(self):
        self.txtFromDate.setEnabled(self.rdCustomTime.isChecked())
        self.txtToDate.setEnabled(self.rdCustomTime.isChecked())

    # def onDownloadAllChecked(self):
    #     """Hàm xử lý sự kiện khi RadioButton thay đổi trạng thái"""
    #      # Hiện lớp phủ
    #     self.txtQuatityDownload.setEnabled(not self.rdDownloadAllVideo.isChecked())
    #     QApplication.processEvents() 
    #     radio_button = self.sender()  # Lấy RadioButton kích hoạt sự kiện
    #     url = self.txtUrl.text()
    #     if not url or not self.is_valid_url(url):
    #         print("Nhập đường dẫn đi")
    #         return
    #     self.getQuantityVideo = QuantityVideoChannel(url)
    #     self.getQuantityVideo.processInfo.connect(self.processGetQuantityVideoChannel)
    #     self.getQuantityVideo.processError.connect(self.processError)
    #     if radio_button.isChecked(): 
    #         if self.getQuantityVideo and self.getQuantityVideo.isRunning():
    #             self.getQuantityVideo.wait()
    #             self.getQuantityVideo.typeRun = 2
    #         self.overlay.show_overlay() 
    #         self.getQuantityVideo.start()

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
        if quantity<=0:
            return
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
    
    