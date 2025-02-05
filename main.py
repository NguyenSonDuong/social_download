import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'message'))
from youtube.youtube_download import Youtube
from youtube.youtube_key import YoutubeKey, Option
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
    

def YoutubeDownloadServerTwo(option_list_video, option_download):

    return



def DouyinDownload():
    print("Update...")

if __name__ == "__main__":

    luachon = input("""
1. Tải video youtube
2: Tải video Douyin
Nhập lựa chọn của bạn: """)
    
    if int(luachon) == 1:
        try:
            success, error = YoutubeDownloadServerOne()
            if len(error)>0:
                youtube_server_2 = YoutubeServerTwo("")
                for video_error in error:
                    status = youtube_server_2.download_video_and_audio(video_error["id"])
        except Exception as e:
            print(e)
            YoutubeDownloadServerTwo(None,None)

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
