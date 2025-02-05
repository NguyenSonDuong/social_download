import yt_dlp
from enum import Enum
import inspect
from message.message import Message
from youtube_key import YoutubeKey

class Youtube:
    
    _prcess = None
    def __init__(self, process = None):
        self._prcess = process
        
        pass

    def quick_sort_view(self, videos):
        try:
            if len(videos) <= 1:
                return videos
            else:
                pivot = videos[len(videos) // 2]['view_count']
                left = [x for x in videos if x['view_count'] < pivot]
                middle = [x for x in videos if x['view_count'] == pivot]
                right = [x for x in videos if x['view_count'] > pivot]
                return self.quick_sort_view(left) + middle + self.quick_sort_view(right)
        except Exception as e:
            raise


    def get_list_video(self, option):
        try:
            ydl_opts = {
                'extract_flat': True,
                'skip_download': True,
                'quiet': True
            }

            if self._prcess:
                self._prcess(Message.NotificationType.NOTIFICATION, f"{Message.Youtube.message_get_info_channel_start}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    channel_info = ydl.extract_info(option["url"], download=False)
                except Exception as e:
                    if self._prcess:
                        self._prcess(Message.NotificationType.ERROR, f"{Message.Youtube.message_get_info_channel_success}: Error: {e}")
                    return []

            if self._prcess:
                self._prcess(Message.NotificationType.NOTIFICATION, f"{Message.Youtube.message_get_info_channel_success}: {channel_info['title']}")
            
            if channel_info['entries'] == None or  "entries" not in channel_info:
                return []
            
            if option['video_type'] == YoutubeKey.VideoType.SHORT and len(channel_info['entries'][1]['entries']) <=0:
                return []
            
            if option['video_type'] == YoutubeKey.VideoType.VIDEO and len(channel_info['entries'][0]['entries']) <=0:
                return []
            
            videos = channel_info['entries'][1]['entries'] if option['video_type'] == YoutubeKey.VideoType.SHORT else channel_info['entries'][0]['entries']

            if option['video_sort'] == YoutubeKey.VideoSort.PHOBIEN:
                videos = self.quick_sort_view(videos)
            elif option['video_sort'] == YoutubeKey.VideoSort.CUNHAT:
                videos = videos[::-1]
            
            if int(option['count']) == -1:
                return videos
            else:
                return videos[0:int(option['count']):1]
        except e:
            if self._prcess:
                self._prcess(Message.NotificationType.ERROR, f"{Message.Youtube.message_get_info_channel_success}: Error: {e}")
        
    def download_video(self, video_url, output_path, video_format = YoutubeKey.VideoFormat[0]):
        ydl_opts = {
            'format': video_format,  
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [self._download_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([video_url]) 
                return True
            except Exception as e:
                if self._prcess:
                    self._prcess(Message.NotificationType.ERROR, f"{Message.Youtube.message_get_info_channel_success}: Error: {e}")
                return False
            
    def _download_hook(self, d):
        pass
        # if d['status'] == 'finished':
        #     print(f"Done downloading {d['filename']}")
        # elif d['status'] == 'downloading':
        #     print(f"Downloading {d['filename']} - {d['_percent_str']} complete")

    def download_videos(self, videos, option=None):
        error_video = []
        success_video = []
        for video in videos:
            if self._prcess:
                self._prcess(Message.NotificationType.NOTIFICATION, f"{Message.Youtube.message_get_info_channel_success}: {video['title']}")
            if self.download_video(video["url"],option["output_path"]):
                success_video.append(video)
            else:
                error_video.append(video)
        return success_video, error_video
                
        

