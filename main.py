import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'message'))
from youtube.youtube_download import Youtube


def process(funtion_name, messgae):
    print(f"{funtion_name}: {messgae}")

youtube = Youtube(process)

list_url_video_of_channel = youtube.get_list_link_video("https://www.youtube.com/channel/UCYb4Rb4Gznn2OkydUS1XTog")

print(list_url_video_of_channel)
