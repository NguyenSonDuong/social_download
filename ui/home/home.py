from PyQt5.QtWidgets import  QMainWindow, QGraphicsDropShadowEffect
from PyQt5 import uic
from youtube.youtube import  Youtube, YoutubeStatus
from PyQt5.QtGui import QColor, QPainter, QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt, QPoint,QEvent
from PyQt5.QtWidgets import QButtonGroup ,QFrame, QVBoxLayout,QLabel,QApplication,QCalendarWidget,QPushButton,QFileDialog
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta
import re
import os
import json
from edit.editvideo import EditVideo, EditStatus
from douyin.douyin_once.douyin import Douyin, DouyinStatus
import logging
import inspect
logging.basicConfig(filename="error.log", level=logging.ERROR)



class WorkerThreadYoutube(QThread):
    # Tạo 4 tín hiệu tương ứng với 4 hàm cần truyền
    processInfo = pyqtSignal(int, int)
    processDownload = pyqtSignal(int,list, list, int)
    processDownloadVideo = pyqtSignal(float, float, float, float, int)
    processError = pyqtSignal(str, list)

    def __init__(self,  url, setting, isEdit = False, isColor = False, isAudio = False):
        super().__init__()
        self.url = url
        self.isEdit = isEdit
        self.isColor = isColor
        self.isAudio = isAudio
        self.setting = setting
        self.isDownload = True

    def get_all_files(self,directory):
        files = []
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isfile(full_path):  # Chỉ lấy file, bỏ qua folder
                files.append(full_path)
        return files
    def run(self):
        """Hàm chạy trong thread"""
        # Tạo đối tượng VideoProcessor và truyền các tín hiệu xuống lớp
        if self.isDownload:
            youtube = Youtube(
                self.processInfo.emit,  
                self.processDownload.emit,  
                self.processError.emit , 
                self.processDownloadVideo.emit
            )
            youtube.run(self.url,self.setting)
        if  self.isEdit or  self.isColor or  self.isAudio:
            edit = EditVideo(
                self.processDownload.emit,
                self.processError.emit,
                self.setting,
                self.isEdit, self.isColor, self.isAudio
            )
            list = self.get_all_files(self.download_folder)
            if len(list) <= 0:
                self.processError.emit("Không tìm thấy file trong thư mục", EditStatus.ERROR)
                return
            i = 0
            success = []
            error = []
            for video in list:
                try:
                    edit.run(video)
                    success.append(video)
                    self.processDownload.emit(len(list), success, error, EditStatus.DONE_ONE)
                except Exception as ex:
                    print(ex)
                    error.append(video)
                    self.processDownload.emit(len(list), success, error, EditStatus.DONE_ONE)
            self.processDownload.emit(len(list), success, error, EditStatus.DONE)
class WorkerThreadDouyin(QThread):
    # Tạo 4 tín hiệu tương ứng với 4 hàm cần truyền
    processInfo = pyqtSignal(int, int)
    processDownload = pyqtSignal(int,list, list, int)
    processError = pyqtSignal(str, int)
    
    def __init__(self,  id, setting, isEdit = False, isColor = False, isAudio = False):
        super().__init__()
        self.id = id
        self.isEdit = isEdit
        self.isColor = isColor
        self.isAudio = isAudio
        self.setting = setting
        self.isDownload = True

    def get_all_files(self,directory):
        files = []
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isfile(full_path):  # Chỉ lấy file, bỏ qua folder
                files.append(full_path)
        return files
    def run(self):
        """Hàm chạy trong thread"""
        # Tạo đối tượng VideoProcessor và truyền các tín hiệu xuống lớp
        if self.isDownload:
            douyin = Douyin(
                self.processInfo.emit,  
                self.processDownload.emit,
                self.processError.emit 
            )
            douyin.run(self.id,self.setting)
        if  self.isEdit or  self.isColor or  self.isAudio:
            edit = EditVideo(
                self.processDownload.emit,
                self.processError.emit,
                self.setting,
                self.isEdit, self.isColor, self.isAudio
            )
            list = self.get_all_files(self.download_folder)
            if len(list) <= 0:
                self.processError("Không tìm thấy file trong thư mục", EditStatus.ERROR)
                return
            i = 0
            success = []
            error = []
            for video in list:

                try:
                    edit.run(video)
                    success.append(video)
                    self.processDownload.emit(len(list), success, error, EditStatus.PROCESS)
                except Exception as ex:
                    error.append(video)
                    self.processDownload.emit(len(list), success, error, EditStatus.PROCESS)
            self.processDownload.emit(len(list), success, error, EditStatus.DONE)

class LoadingOverlay(QFrame):
    def __init__(self, parent=None, gif_path="loading.gif"):
        super().__init__(parent)
        self.resize(parent.size())
        self.threadYoutube = None
        self.threadDouyin = None
        self.setUIUX()

    def setUIUX(self):
        try:
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
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")

    def setOverlayGeometry(self, target_widget):
        try:
            self.setGeometry(target_widget.geometry())  
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
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
        "count_download":"",
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
            "opacity":None,
            "red":None,
            "green":None,
            "blue":None,
            "birghtness":None,
            "color_custom":None,
            "saturation":None,
            "gamma":None,
            "hue":None,
            "audio_tone":None
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
        try:
            uic.loadUi("ui/home/home.ui",self)
            self.isRunEdit = False
            self.isEditVideo = False
            self.isEditColor = False
            self.isEditAudio = False


            self._drag_active = False
            self._drag_position = QPoint()

            self.resize(1450, 865) 

            self.overlay = LoadingOverlay(self, "loading.gif")

            self.setAndRun()

            self.threadYoutube = None
            self.threadDouyin = None

            self.typeDownload = "Douyin"
            
            self.overlay.hide_overlay()
            self.overlay.setOverlayGeometry(self.mainLayout) 
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex
    
    # Kiểm tra đầu vào

    def validInt(self,text):
        return bool(re.fullmatch(r"-?\d+(\.\d+)?", text))
    def validPath(self,path):
        pattern = r"^([a-zA-Z]:\\|/)?([\w\s.-]+[/\\]?)+$"
        return bool(re.fullmatch(pattern, path))
    def checkValidTextbox(self, type = "Video"):
        try:

            if type == "Video":
                if self.txtSppedCustom.text() and not self.validInt(self.txtSppedCustom.text()) :
                    self.lbErrorSpeed.show()
                    return False
                
                if  self.txtCutEnd.text() and not self.validInt(self.txtCutEnd.text()) :
                    self.lbErrrorCut.show()
                    return False
                
                if self.txtCutStart.text() and not self.validInt(self.txtCutStart.text()) :
                    self.lbErrrorCut.show()
                    return False
                
                
                if self.txtFolderSave.text() and not self.validPath(self.txtFolderSave.text()) :
                    self.lbErrorFolderSave.show()
                    return False
            
            # đây là dành cho intro và outro
                
                if self.txtInto.text() and not self.validPath(self.txtInto.text()) :
                    self.lbErrorIntro.show()
                    return False
                
                
                if self.txtOutro.text() and not self.validPath(self.txtOutro.text()) :
                    self.lbErrorOutro.show()
                    return False
            
            # đây là dành cho video ngang và dọc
            
                if self.txtRowVideoLeft.text() and not self.validPath(self.txtRowVideoLeft.text()) :
                    self.lbErrorRowLeft.show()
                    return False
                
                
                if self.txtRowVideoRight.text() and not self.validPath(self.txtRowVideoRight.text()) :
                    self.lbErrorRowRight.show()
                    return False
                
                
                if self.txtColumLeft.text() and not self.validPath(self.txtColumLeft.text()) :
                    self.lbErrorErrorLeftVideoCollum.show()
                    return False
                
                
                if self.txtColumRight.text() and not self.validPath(self.txtColumRight.text()) :
                    self.lbErrorErrorRightVideoCollum.show()
                    return False
            if type == "Color":
            # đây là cho chỉnh sửa màu sắc

                if self.txtOpacity.text() and not self.validInt(self.txtOpacity.text()) :
                    self.lbErrorBaseColor.show()
                    return False

                if self.txtRed.text() and not self.validInt(self.txtRed.text()) :
                    self.lbErrorBaseColor.show()
                    return False

                if self.txtGreen.text() and not self.validInt(self.txtGreen.text()) :
                    self.lbErrorBaseColor.show()
                    return False

                if self.txtBlue.text() and not self.validInt(self.txtBlue.text()) :
                    self.lbErrorBaseColor.show()
                    return False

                if self.txtBrightness.text() and not self.validInt(self.txtBrightness.text()) :
                    self.lbErrorBaseColor.show()
                    return False

                if self.txtColorCustom.text() and not self.validInt(self.txtColorCustom.text()) :
                    self.lbErrorBaseColor.show()
                    return False

                if self.txtSatuation.text() and not self.validInt(self.txtSatuation.text()) :
                    self.lbErrorAdvColor.show()
                    return False

                if self.txtGamma.text() and not self.validInt(self.txtGamma.text()) :
                    self.lbErrorAdvColor.show()
                    return False

                if self.txtHue.text() and not self.validInt(self.txtHue.text()) :
                    self.lbErrorAdvColor.show()
                    return False

                if self.txtAudioTone_2.text() and not self.validInt(self.txtAudioTone_2.text()) :
                    self.lbErrorAdvColor.show()
                    return False
            # đây là cho sửa âm thanh
            if type == "Audio":
                if self.txtMainVolum.text() and not self.validInt(self.txtMainVolum.text()) :
                    return False

                if self.txtAudioTone.text() and not self.validInt(self.txtAudioTone.text()) :
                    return False

                if self.txtEditAudio.text() and not self.validInt(self.txtEditAudio.text()) :
                    return False

                if self.txtFadeIn.text() and not self.validInt(self.txtFadeIn.text()) :
                    return False
                
                if self.txtFadeOut.text() and not self.validInt(self.txtFadeOut.text()) :
                    return False
                return True
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            return False
    
    # cài đặt giá trị cho các textbox
    def setupDownloadVideoSetting(self):
        try:
            if self.setting["type_download"] == "1":
                self.rdFullChannel.setChecked(True)
            if self.setting["type_download"] == "2":
                self.rdDownloadFromLink.setChecked(True)
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
            if self.setting["count_download"]:
                self.txtQuatityDownload.setText(self.setting["count_download"])
            if self.setting["folder_save_video"]:
                self.txtFolderSaveVideo.setText(self.setting["folder_save_video"])
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
    def setupEditVideoSetting(self):
        try:
            if not self.checkValidTextbox("Video"):
                return
            # chọn khung hingf
            if self.setting["edit_video"]["frame"] == "1":
                self.rd169.setChecked(True)
            elif self.setting["edit_video"]["frame"] == "2":
                self.rd619.setChecked(True)
            elif self.setting["edit_video"]["frame"] == "3":
                self.rd43.setChecked(True)
            elif self.setting["edit_video"]["frame"] == "0":
                self.rdFrameNoChange.setChecked(True)

            # chọn tốc độ video
            if self.setting["edit_video"]["speed_video"] == "0":
                self.rdSpeedKeep.setChecked(True)
            if self.setting["edit_video"]["speed_video"] == "1":
                self.rdSpeedx2.setChecked(True)
            if self.setting["edit_video"]["speed_video"] == "2":
                self.rdSpeedx4.setChecked(True)
            self.txtSppedCustom.setText(self.setting["edit_video"]["speed_video_custom"])

            # chọn cắt video
            if self.setting["edit_video"]["cut_video"] == "1":
                self.rdCut3sStart.setChecked(True)
            elif self.setting["edit_video"]["cut_video"] == "2":
                self.rdCutSpped3sEnd.setChecked(True)
            elif self.setting["edit_video"]["cut_video"] == "3":
                self.rdCut1sForeach5s.setChecked(True)
            elif self.setting["edit_video"]["cut_video"] == "0":
                self.rgCutNoChange.setChecked(True)
            self.txtCutStart.setText(self.setting["edit_video"]["cut_video_custom"]["start"])
            self.txtCutEnd.setText(self.setting["edit_video"]["cut_video_custom"]["end"])

            # chọn thư mục lưu video
            self.txtFolderSave.setText(self.setting["edit_video"]["save_folder_edit_video"])

            # chọn intro và outro
            self.txtInto.setText(self.setting["edit_video"]["intro_video"])
            self.txtOutro.setText(self.setting["edit_video"]["outro_video"])

            #chọn video trên và dưới
            self.txtRowVideoTop.setText(self.setting["edit_video"]["top_video"])
            self.txtRowVideoDown.setText(self.setting["edit_video"]["bottom_video"])

            # chọn video trái và phải
            self.txtColumLeft.setText(self.setting["edit_video"]["left_video"])
            self.txtColumRight.setText(self.setting["edit_video"]["right_video"])
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex
    def setupEditColorSetting(self):
        try:
            if not self.checkValidTextbox("Color"):
                return
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
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex
    def setupEditAudioSetiing(self):
        try:
            if not self.checkValidTextbox("Audio"):
                return
            self.txtMainVolum.setText(self.setting["audio"]["main_volum"])
            self.txtAudioTone.setText(self.setting["audio"]["audio_tone"])
            self.txtNumberVolum.setText(self.setting["audio"]["volum_all"])

            self.txtFolderMusicVideo.setText(self.setting["audio"]["mix_audio"])

            self.txtEditAudio.setText(self.setting["audio"]["edit_audio"])
            self.txtFadeIn.setText(self.setting["audio"]["fade_in"])
            self.txtFadeOut.setText(self.setting["audio"]["fade_out"])
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex


    def setupdSetting(self):
        self.setupDownloadVideoSetting()
        self.setupEditColorSetting()
        self.setupEditVideoSetting()
        self.setupEditAudioSetiing()

    def saveDownloadSetting(self):
        try:
            self.setting["type_download"] = "1" if self.rdFullChannel.isChecked() else "2" if self.rdDownloadFromLink.isChecked() else "3"
            self.setting["order_download"] = "1" if self.rdDownloadNewVideo.isChecked() else "2" if self.edDownloadTrending.isChecked() else "3" if self.rdDownloadOld.isChecked() else "4" if self.rdDownloadDate.isChecked() else "5" if self.rdDownloadWeek.isChecked() else "6"
            self.setting["folder_save_video"] = self.txtFolderSaveVideo.text()
            self.setting["count_download"] = self.txtQuatityDownload.text()
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def saveEditVideoSetting(self):
        try:
            if not self.checkValidTextbox("Video"):
                return
            self.setting["edit_video"]["frame"] = "1" if self.rd169.isChecked() else "2" if self.rd619.isChecked() else 3 if self.rd43.isChecked() else "0"
            self.setting["edit_video"]["speed_video"] = "1" if self.rdSpeedKeep.isChecked() else "2" if self.rdSpeedx2.isChecked() else "3" 
            self.setting["edit_video"]["cut_video"] = "1" if self.rdCut3sStart.isChecked() else "2" if self.rdCutSpped3sEnd.isChecked() else "3" if self.rdCut1sForeach5s.isChecked() else "0"
            self.setting["edit_video"]["cut_video_custom"]["start"] = self.txtCutStart.text()
            self.setting["edit_video"]["cut_video_custom"]["end"] = self.txtCutEnd.text()
            self.setting["edit_video"]["intro_video"] = self.txtInto.text()
            self.setting["edit_video"]["outro_video"] = self.txtOutro.text()
            self.setting["edit_video"]["left_video"] = self.txtRowVideoLeft.text()
            self.setting["edit_video"]["right_video"] = self.txtRowVideoRight.text()
            self.setting["edit_video"]["top_video"] = self.txtColumLeft.text()
            self.setting["edit_video"]["bottom_video"] = self.txtColumRight.text()
            self.setting["edit_video"]["save_folder_edit_video"] = self.txtFolderSave.text()
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def saveEditAudioSetting(self):
        try:
            if not self.checkValidTextbox("Audio"):
                return
            self.setting["audio"]["main_volum"] = self.txtMainVolum.text()
            self.setting["audio"]["audio_tone"] = self.txtAudioTone.text()
            self.setting["audio"]["volum_all"] = self.txtNumberVolum.text()
            self.setting["audio"]["mix_audio"] = self.txtFolderMusicVideo.text()
            self.setting["audio"]["edit_audio"] = self.txtEditAudio.text()
            self.setting["audio"]["fade_in"] = self.txtFadeIn.text()
            self.setting["audio"]["fade_out"] = self.txtFadeOut.text()
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def saveEditColorSetting(self):
        try:
            if not self.checkValidTextbox("Color"):
                return
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
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def is_folder(self,path):
        return os.path.isdir(path)

    def log(self, text, color="red"):
        cursor = self.overlay.frame.txtLog.textCursor()
        red_format = QTextCharFormat()
        red_format.setForeground(QColor(color))
        cursor.insertText(f"{text}\n", red_format)

    def processInfo(self, numberVideo, status):
        try:
            print(f"Đã lấy được thông tin của: {numberVideo}")
            self.log(f"Đã lấy được thông tin của: {numberVideo} video","green")
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def processDownload(self,total, videoDownload, videoError,status):
        try:
            if status == DouyinStatus.DOUYIN_PROCESS:
                self.log(f"Đang tải video: {videoDownload[0]['desc']}","blue")
            if status == DouyinStatus.DONE_ONE:
                self.log(f"tải xong video: {videoDownload[0]['desc']}","green")
            if status == YoutubeStatus.DONE_ONE:
                try:
                    self.log(f"Đã tải xong: {videoDownload[0]["title"]}","green")
                except Exception as ex:
                    self.overlay.frame.pnAllsBar.setMaximum(total)
                    self.overlay.frame.pnAllsBar.setValue(len(videoDownload)+len(videoError))
                print(f"Đã tải được: {len(videoDownload)} - Video tải lỗi: {len(videoError)} - {status}")
            if status == YoutubeStatus.PROCESS:
                self.overlay.frame.pnAllsBar.setMaximum(total)
                self.overlay.frame.pnAllsBar.setValue(len(videoDownload)+len(videoError))
                print(f"Đã tải được: {len(videoDownload)} - Video tải lỗi: {len(videoError)} - {status}")
            if status == YoutubeStatus.DONE:
                self.overlay.hide_overlay()
            if status == YoutubeStatus.ERROR:
                self.log("Lỗi lấy thông số video! ")
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def processDownloadVideo(self,percent,speed,downloaded,total,status):
        try:
            if status == YoutubeStatus.PROCESS:
                self.overlay.frame.pnChildensBar.setMaximum(100)
                self.overlay.frame.pnChildensBar.setValue(int(percent))
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex

    def processError(self, error, status):
        try:
            self.log(str(error))
            print(error)
        except Exception as ex:
            logging.error(f"FUNCTION: {inspect.currentframe().f_code.co_name} - {ex}")
            raise ex
        

    def startTaskYoutube(self, url,count, order, from_date, to_date, download_folder, isDownload = True):

        """Khởi chạy tiến trình"""
        if self.isRunEdit:
            if self.threadYoutube  and self.threadYoutube.isRunning():
                self.threadYoutube.wait()
                self.threadYoutube.typeRun = 1
            self.threadYoutube = WorkerThreadYoutube(url,self.setting,self.isEditVideo, self.isEditColor, self.isEditAudio)
        else:
            if self.threadYoutube  and self.threadYoutube.isRunning():
                self.threadYoutube.wait()
                self.threadYoutube.typeRun = 1
            self.threadYoutube = WorkerThreadYoutube(url,self.setting,False, False, False)
        # Kết nối tín hiệu từ Thread đến các hàm giao diện
        self.threadYoutube.processInfo.connect(self.processInfo)
        self.threadYoutube.processDownload.connect(self.processDownload)
        self.threadYoutube.processDownloadVideo.connect(self.processDownloadVideo)
        self.threadYoutube.processError.connect(self.processError)
        self.overlay.threadYoutube = self.threadYoutube
        self.threadYoutube.isDownload = isDownload
        self.threadYoutube.start()

    def startTaskDouyin(self, url,count, from_date, to_date, download_folder, isDownload = True):
        """Khởi chạy tiến trình"""
        if self.isRunEdit:
            if self.threadDouyin  and self.threadDouyin.isRunning():
                self.threadDouyin.wait()
                self.threadDouyin.typeRun = 1
            self.threadDouyin = WorkerThreadDouyin(url,self.setting,self.isEditVideo, self.isEditColor, self.isEditAudio)
        else:
            if self.threadDouyin  and self.threadDouyin.isRunning():
                self.threadDouyin.wait()
                self.threadDouyin.typeRun = 1
            self.threadDouyin = WorkerThreadDouyin(url,self.setting,False, False, False)
        # Kết nối tín hiệu từ Thread đến các hàm giao diện
        self.threadDouyin.processInfo.connect(self.processInfo)
        self.threadDouyin.processDownload.connect(self.processDownload)
        self.threadDouyin.processError.connect(self.processError)
        self.overlay.threadDouyin = self.threadDouyin
        self.threadDouyin.isDownload = isDownload
        self.threadDouyin.start()   

    def onBtnRunWithoutEditClick(self,event):
        self.RunMain(False,True)
    def onBtnRunWithoutDonloadClick(self,event):
        self.RunMain(True,False)
    def onBtnRunClick(self,event):
        self.RunMain(True, True)
        
        
    def RunMain(self, isRunEdit, isDownload = True):

        self.isRunEdit = isRunEdit
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
        self.saveDownloadSetting()
        self.overlay.show_overlay()
        if self.typeDownload == "Youtube":
            self.startTaskYoutube(url,quantity,order,from_date,to_date,folder_download,isDownload)
        if self.typeDownload == "Douyin":
            pattern = r"user/(MS4wLj[A-Za-z0-9_-]+)"
            match = re.search(pattern, url)
            if match:
                user_id = match.group(1)
                self.startTaskDouyin(user_id,quantity,from_date,to_date,folder_download,isDownload)
            else:
                print("Không tìm thấy User ID")
                self.log("Không tìm thấy User ID! vui lòng kiểm tra lại đường dẫn")
                self.lbErrorUrl.show()
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

        self.setupDownloadVideoSetting()
        self.setupLayout()
        self.setupCalendar()
        self.setupNavigator()

        self.setupShadowsForTheme()
        self.setupGroupCheckbox()
        
        self.btnRun.clicked.connect(self.onBtnRunClick)
        self.btnRunWithoutEdit.clicked.connect(self.onBtnRunWithoutEditClick)
        self.btnRunWithoutDownload.clicked.connect(self.onBtnRunWithoutDonloadClick)


        self.btnSelectFolder.clicked.connect(self.onBtnSelectFolderClick)
        self.btnSelectFolderSaveEdit.clicked.connect(self.onBtnSelectFolderSaveEditClick)

        self.btnSaveEditVideo.clicked.connect(self.onBtnSaveEditVideoClick)
        self.btnEditColorVideo.clicked.connect(self.onBtnEditColorVideoClick)
        self.btnSaveAudioSetting.clicked.connect(self.onBtnSaveAudioSettingClick)


        self.btnEditVideo.clicked.connect(self.onBtnEditVideoClick)
        self.btnEditColor.clicked.connect(self.onBtnSaveEditColorClick)
        self.btnEditAudio.clicked.connect(self.onBtnEditAudioClick)
        
        self.lbErrorUrl.hide()
        self.lbErrorQuantity.hide()
        self.lbErrorSelectFolder.hide()
        self.loadSettingFromFile()
        self.setupdSetting()

        shadow = QGraphicsDropShadowEffect(self.btnDouyin)
        shadow.setBlurRadius(15)  
        shadow.setOffset(3, 3)  
        shadow.setColor(QColor(0, 0, 0, 100)) 
        self.btnDouyin.setGraphicsEffect(shadow)  

        if self.isEditVideo:
            self.editMainLayout.show()
        else:
            self.editMainLayout.hide()
        if self.isEditColor:
            self.editColorMainLayout.show()
        else:
            self.editColorMainLayout.hide()
        if self.isEditAudio:
            self.editAudioMainLayout.show()
        else:
            self.editAudioMainLayout.hide()

        self.lbErrorSpeed.hide()
        self.lbErrrorCut.hide()
        self.lbErrorFolderSave.hide()

        self.lbErrorIntro.hide()
        self.lbErrorOutro.hide()
        self.lbErrorRowLeft.hide()
        self.lbErrorRowRight.hide()
        self.lbErrorErrorLeftVideoCollum.hide()
        self.lbErrorErrorRightVideoCollum.hide()
        self.lbErrorBaseColor.hide()
        self.lbErrorAdvColor.hide()

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

    def onBtnEditVideoClick(self, event):
        if self.editMainLayout.isHidden():
            self.editMainLayout.show()
            self.isEditVideo = True
        else:
            self.isEditVideo = False
            self.editMainLayout.hide()

    def onBtnSaveEditColorClick(self, event):
        if self.editColorMainLayout.isHidden():
            self.editColorMainLayout.show()
            self.isEditColor = True
        else:
            self.isEditColor = False
            self.editColorMainLayout.hide()

    def onBtnEditAudioClick(self, event):
        if self.editAudioMainLayout.isHidden():
            self.editAudioMainLayout.show()
            self.isEditAudio = True
        else:
            self.isEditAudio = False
            self.editAudioMainLayout.hide()

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

    def onBtnSelectFolderClick(self,event):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục", "")
        
        if folder_path:  # Nếu người dùng chọn thư mục
            self.txtFolderSaveVideo.setText(f"{folder_path}")

    def onBtnSelectFolderSaveEditClick(self,event):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục", "")
        
        if folder_path:  # Nếu người dùng chọn thư mục
            self.txtFolderSave.setText(f"{folder_path}")

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
                if obj == self.btnDouyin:
                    self.typeDownload = "Douyin"
                    self.rdDownloadOld.setEnabled(False)
                    self.rdDownloadOld.setChecked(False)
                if obj == self.btnYoutube:
                    self.typeDownload = "Youtube"
                    self.rdDownloadOld.setEnabled(True)
        
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
    
    