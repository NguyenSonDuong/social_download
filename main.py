import sys
import os
from PyQt5.QtWidgets import QApplication
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'message'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'youtube'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ui'))
from youtube.youtube_download import Youtube
from youtube.youtube_key import  Option, YoutubeKey
from youtube.youtube_download_server_2 import YoutubeServerTwo
from ui.home.home import Ui_HomeWindow
from douyin.douyin_server_one import Douyin
def process(funtion_name, messgae):
    print(f"{funtion_name}: {messgae}")

                                                 
def YoutubeDownloadServerOne(option = Option()):
    youtube = Youtube(process, option)
    list_url_video_of_channel = youtube.get_list_video()
    if(len(list_url_video_of_channel)<=0):
        raise Exception("List video empty !!!")
    success, error = youtube.download_videos(list_url_video_of_channel)
    return success, error
    

def YoutubeDownloadServerTwo(option):
    youtube = YoutubeServerTwo(process,option)
    youtube.run()
    return

def DouyinDownload(option):
    douyin  = Douyin(process,option)
    video, error_link =  douyin.get_page_sources()
    douyin.download_video(video)
    print("Update...")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    home = Ui_HomeWindow(YoutubeDownloadServerOne,DouyinDownload)
    sys.exit(app.exec_())
   





# def SetOption():
#     option = Option()
#     API_KEY = input("Nhập API_KEY (Nếu không có nhấn Enter): ")
#     if len(API_KEY)>= 10:
#         option.API_KEY = API_KEY
#     option.channel_url = input("Nhập url channel: ")
#     print("=================================================\n")

#     option.video_sort = int(input("""
# "1". Video phổ biến
# "2". Video cũ
# "3". Video mới nhất
# Nhập lựa chọn của bạn: """))
#     print("=================================================\n")
    
#     option.video_type = int(input("""
# "1". Video
# "2". Short
# Nhập lựa chọn của bạn: """))
#     print("=================================================\n")

#     option.video_duration = int(input("""Nhập loại video:
# '1': All video
# '2': Video lớn hơn 20phút
# '3': Video từ 4-20 phút
# '4': Video 1-4p
# '5': Video dưới 1phút
# Nhập lựa chọn của bạn:  """))
#     print("=================================================\n")
#     option.count = int(input("Nhập số lượng video (nhập -1 nếu muốn tải tất): "))

#     format = input("""
# "0". Video chất lượng cao
# "1". Video chất lượng thấp
# "2". Video chất lượng cao (Không có âm thanh)
# "3". Video chất lượng thấp (Không có âm thanh)
# "4". Audio chất lượng cao (Không có video)
# "5". Audio chất lượng thấp (Không có video)
# Nhập lựa chọn của bạn: """)
#     option.video_quatity = YoutubeKey.VideoQuality.VideoFormat[int(format)]
#     return option
