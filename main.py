import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'message'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'youtube'))
from youtube.youtube_download import Youtube
from youtube.youtube_key import  Option
from youtube.youtube_download_server_2 import YoutubeServerTwo

def process(funtion_name, messgae):
    print(f"{funtion_name}: {messgae}")


def YoutubeDownloadServerOne(option = Option()):

    youtube = Youtube(process, option)
#
    list_url_video_of_channel = youtube.get_list_video()

    if(len(list_url_video_of_channel)<=0):
        raise Exception("List video empty !!!")

    success, error = youtube.download_videos(list_url_video_of_channel)

    return success, error
    

def YoutubeDownloadServerTwo(option):

    return

def SetOption():
    option = Option()
    API_KEY = input("Nhập API_KEY (Nếu không có nhấn Enter): ")
    if len(API_KEY)>= 10:
        option.API_KEY = API_KEY
    option.channel_url = input("Nhập url channel: ")
    print("=================================================\n")

    option.video_sort = int(input("""
"1". Video phổ biến
"2". Video cũ
"3". Video mới nhất
Nhập lựa chọn của bạn: """))
    print("=================================================\n")
    
    option.video_type = int(input("""
"1". Video
"2". Short
Nhập lựa chọn của bạn: """))
    print("=================================================\n")

    option.video_duration = int(input("""Nhập loại video:
'1': All video
'2': Video lớn hơn 20phút
'3': Video từ 4-20 phút
'4': Video 1-4p
'5': Video dưới 1phút
Nhập lựa chọn của bạn:  """))
    print("=================================================\n")
    option.count = int(input("Nhập số lượng video (nhập -1 nếu muốn tải tất): "))

    format = input("""
"0". Video chất lượng cao
"1". Video chất lượng thấp
"2". Video chất lượng cao (Không có âm thanh)
"3". Video chất lượng thấp (Không có âm thanh)
"4". Audio chất lượng cao (Không có video)
"5". Audio chất lượng thấp (Không có video)
Nhập lựa chọn của bạn: """)
    option.video_quatity = int(format)
    return option

def DouyinDownload():
    print("Update...")

if __name__ == "__main__":

    luachon = input("""
1. Tải video youtube
2: Tải video Douyin
Nhập lựa chọn của bạn: """)

    if int(luachon) == 1:
        option = SetOption()
        try:
            success, error = YoutubeDownloadServerOne(option)
            if len(error)>0:
                youtube_server_2 = YoutubeServerTwo(option)
                for video_error in error:
                    status = youtube_server_2.download_video_and_audio(video_error["id"])
        except Exception as e:
            print(e)
            YoutubeDownloadServerTwo(option)

    if int(luachon) == 2: 
        DouyinDownload()
    


    #  option_list_video ={
#                 "url": "",
#                 "video_sort": VideoSort.PHOBIEN,
#                 "video_type": VideoType.VIDEO,
#                 "count": -1
#             }
#     option_list_video["url"] = input("Nhập url channel: ")
#     option_list_video["video_sort"] = input("""
# 1. Video phổ biến
# 2. Video cũ
# 3. Video mới nhất
# Nhập lựa chọn của bạn: """)
#     option_list_video["video_type"] = input("""
# 1. Video
# 2. Short
# Nhập lựa chọn của bạn: """)
#     option_list_video["count"] = input("Nhập số lượng video (nhập -1 nếu muốn tải tất): ")

    # option_download = {
    #     "format": "best",
    #     "output_path": "download"
    # }

#     format = input("""
# 0. Video chất lượng cao
# 1. Video chất lượng thấp
# 2. Video chất lượng cao (Không có âm thanh)
# 3. Video chất lượng thấp (Không có âm thanh)
# 4. Audio chất lượng cao (Không có video)
# 5. Audio chất lượng thấp (Không có video)
# Nhập lựa chọn của bạn: """)
#     option_download["format"] = Youtube.VideoFormat[int(format)]
