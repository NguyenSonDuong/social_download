import yt_dlp
from enum import Enum
import inspect
from message.message import Message

class VideoSort(Enum):
    PHOBIEN = 1
    MOINHAT = 2
    CUNHAT = 3
class VideoType(Enum):
    VIDEO = 0
    SHORT = 1



class Youtube:

    _prcess = None
    def __init__(self, process = None):
        self._prcess = process
        pass

    def quick_sort_view(self, videos):
        if len(videos) <= 1:
            return videos
        else:
            pivot = videos[len(videos) // 2]['view_count']
            left = [x for x in videos if x['view_count'] < pivot]
            middle = [x for x in videos if x['view_count'] == pivot]
            right = [x for x in videos if x['view_count'] > pivot]
            return self.quick_sort_view(left) + middle + self.quick_sort_view(right)


    def get_list_link_video(self, channel_url=None, option=None):
        if channel_url:
            self.channel_url = channel_url
        if option is None:
            option = {
                "video_sort": VideoSort.PHOBIEN,
                "video_type": VideoType.VIDEO,
                "count": 10,
                "time_start": None,
                "time_end": None
            }

        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                channel_info = ydl.extract_info(self.channel_url, download=False)
            except Exception as e:
                print(f"Error: {e}")
                return []

        if self._prcess:
            self._prcess(inspect.currentframe().f_code.co_name, f"{Message.Youtube.message_get_info_channel_success}: {channel_info['title']}")

        print(f'Fetching video URLs from channel: {channel_info["title"]}')

        # Lấy danh sách video và sắp xếp theo thời gian đăng từ mới nhất tới cũ nhất
        
        videos = self.quick_sort_view(channel_info['entries'][1]['entries'] if option["video_type"] == VideoType.SHORT else channel_info['entries'][0]['entries'])

        # Lấy URL và thời gian đăng của các video đã sắp xếp
        video_info = [(video['url'], video['upload_date']) for video in videos]

        for url, upload_date in video_info:
            print(f'URL: {url}, Upload Date: {upload_date}')

        return video_info
    