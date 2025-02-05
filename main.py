import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'message'))
from youtube.youtube_download import Youtube,  VideoSort, VideoType


def process(funtion_name, messgae):
    print(f"{funtion_name}: {messgae}")


def YoutubeDownloadServerOne(option_list_video, option_download):

    youtube = Youtube(process)
#     option_list_video ={
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

    list_url_video_of_channel = youtube.get_list_video(option_list_video)

    if(len(list_url_video_of_channel)<=0):
        return False

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

    success, error = youtube.download_videos(list_url_video_of_channel,option_download)

    if(len(error)>0):
        return False
    else:
        return True

def DouyinDownload():
    print("Update...")

if __name__ == "__main__":

    luachon = input("""
1. Tải video youtube
2: Tải video Douyin
Nhập lựa chọn của bạn: """)
    
    if int(luachon) == 1:
        if not YoutubeDownloadServerOne(None,None):
            print("Dont success")
    if int(luachon) == 2: 
        DouyinDownload()
    


