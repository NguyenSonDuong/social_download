import os
import requests
import re
import subprocess
import time
from pytubefix import YouTube
from pytubefix import cipher
from tqdm import tqdm  # Hiển thị tiến trình tải video
import sys
from message.message import Message
from youtube_key import YoutubeKey
# "AIzaSyC6XAJGYvbDHiLYFGpv8BpUz9PRSNwIQEA"
class YoutubeServerTwo:

    _process = None
    def __init__(self, process, API_KEY ):
        self.VIDEO_TEMP_PATH = './settings/video_temp'
        self.VIDEO_DOWNLOAD_PATH = './video_download'
        self.API_KEY = API_KEY
        self._process = process
        os.makedirs(self.VIDEO_TEMP_PATH, exist_ok=True)
        os.makedirs(self.VIDEO_DOWNLOAD_PATH, exist_ok=True)
        

    #================================ Lấy data video ===========================

    def get_channel_id(self,channel_url):
        """Trích xuất ID kênh từ URL kênh YouTube"""
        match = re.search(r"@([\w-]+)", channel_url)
        if not match:
            return None
        channel_name = match.group(1)

        # Gọi API để lấy ID kênh
        url = f"https://www.googleapis.com/youtube/v3/search?part=id&q={channel_name}&type=channel&key={self.API_KEY}"
        response = requests.get(url).json()

        if "items" in response and response["items"]:
            return response["items"][0]["id"]["channelId"]
        
        return None

    def parse_duration(self,duration):
        """Chuyển đổi thời gian từ ISO 8601 (PT10M15S) sang giây"""
        match = re.search(r"PT(\d+H)?(\d+M)?(\d+S)?", duration)
        total_seconds = 0

        if match:
            hours = int(match.group(1)[:-1]) * 3600 if match.group(1) else 0
            minutes = int(match.group(2)[:-1]) * 60 if match.group(2) else 0
            seconds = int(match.group(3)[:-1]) if match.group(3) else 0
            total_seconds = hours + minutes + seconds

        return total_seconds

    def get_video_details(self,video_ids):
        """Lấy thời lượng video để phân loại"""
        url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={','.join(video_ids)}&key={self.API_KEY}"
        response = requests.get(url).json()
        
        video_info = {}
        
        for item in response.get("items", []):
            video_id = item["id"]
            duration = self.parse_duration(item["contentDetails"]["duration"])
            video_info[video_id] = duration
        
        return video_info

    def get_videos(self,channel_id,option_list_video):
        """Lấy danh sách video từ kênh theo các tiêu chí"""
        
        order_mapping = { 1: "viewCount", 2: "date", 3: "date"}
        order = order_mapping.get(int(option_list_video["video_sort"]), "date")

        video_list = []
        next_page_token = ""
        
        while True:
            # 🔹 Gọi API lấy video
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&key={self.API_KEY}&order={order}&maxResults=50&type=video&pageToken={next_page_token}"
            response = requests.get(url).json()
            
            if "items" not in response:
                break

            video_ids = [item["id"]["videoId"] for item in response["items"] if "videoId" in item["id"]]
            video_durations = self.get_video_details(video_ids)

            for video_id in video_ids:
                duration = video_durations.get(video_id, 0)

                # 🔹 Lọc video theo loại mong muốn
                if  option_list_video["video_duration"]== YoutubeKey.VideoDuaration.VIDEODURATION_20MINUTE and duration <= 1200:
                    continue  # Loại bỏ video ngắn hơn 20 phút
                if option_list_video["video_duration"] == YoutubeKey.VideoDuaration.VIDEODURATION_FROM4TO20MINUTE and (duration < 240 or duration > 1200):
                    continue  # Loại bỏ video không trong khoảng 4-20 phút
                if option_list_video["video_duration"] == YoutubeKey.VideoDuaration.VIDEODURATION_FROM1TO4MINUTE and duration >= 240:
                    continue  # Loại bỏ video dài hơn 4 phút
                if option_list_video["video_duration"] == YoutubeKey.VideoDuaration.VIDEODURATION_UNDER1MINUTE and duration >= 60:
                    continue  # Loại bỏ video không phải Shorts

                video_list.append(video_id)

            # 🔹 Nếu chỉ lấy số lượng nhất định, dừng khi đủ
            if int(option_list_video["count"]) > 0 and len(video_list) >= int(option_list_video["count"]):
                break

            # 🔹 Nếu có trang tiếp theo, tiếp tục lấy
            next_page_token = response.get("nextPageToken", "")
            if not next_page_token or int(option_list_video["count"]) == -1:
                break

        return video_list[0:int(option_list_video["count"])] if int(option_list_video["count"]) == -1 else video_list


    #================================ Xử lý Video ===========================

    # Xử lý lỗi Regex khi tải video
    class RegexMatchError(Exception):
        def __init__(self, caller, pattern):
            self.caller = caller
            self.pattern = pattern
            super().__init__(f"RegexMatchError in {caller}: pattern '{pattern}' not matched.")

    def get_throttling_function_name(self,js: str) -> str:
        """Xử lý thuật toán tải YouTube"""
        function_patterns = [
            r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
            r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
            r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)'
        ]
        for pattern in function_patterns:
            regex = re.compile(pattern)
            function_match = regex.search(js)
            if function_match:
                if len(function_match.groups()) == 1:
                    return function_match.group(1)
                idx = function_match.group(2)
                if idx:
                    idx = idx.strip("[]")
                    array = re.search(
                        rf'var {re.escape(function_match.group(1))}\s*=\s*(\[.+?\]);', js
                    )
                    if array:
                        array = array.group(1).strip("[]").split(",")
                        return array[int(idx)]
        raise self.RegexMatchError(caller="get_throttling_function_name", pattern="multiple")

    cipher.get_throttling_function_name = get_throttling_function_name

    def sanitize_filename(self,filename):
        """Xóa ký tự đặc biệt trong tên file."""
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def download_video_and_audio(self,video_id, resolution='1080p'):
        """Tải video từ YouTube và ghép âm thanh."""
        url = f'https://youtube.com/watch?v={video_id}'
        # url = f'https://www.youtube.com/shorts/{video_id}'
        try:
            yt = YouTube(url)
            safe_title = self.sanitize_filename(yt.title)
            output_file = os.path.join(self.VIDEO_DOWNLOAD_PATH, f"{safe_title}.mp4")
            
            if os.path.exists(output_file):
                print(f"Bỏ qua {safe_title} vì đã tải xuống.")
                return
            
            video_stream = yt.streams.filter(file_extension='mp4', res=resolution, only_video=True).first()
            audio_stream = yt.streams.filter(only_audio=True).first()

            if video_stream and audio_stream:
                video_file = video_stream.download(output_path=self.VIDEO_TEMP_PATH, filename='video.mp4')
                audio_file = audio_stream.download(output_path=self.VIDEO_TEMP_PATH, filename='audio.mp4')
                
                command = f'ffmpeg -hide_banner -loglevel error -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"'
                subprocess.run(command, shell=True, check=True)
                
                os.remove(video_file)
                os.remove(audio_file)
                print(f"✅ Tải xong: {safe_title}")
            else:
                print(f"⚠️ Không tìm thấy stream phù hợp cho {safe_title}")
        except Exception as e:
            print(f'❌ Lỗi tải video {video_id}: {e}')

    def run(self, option_list_video):

        channel_id = self.get_channel_id(option_list_video["url"])

        if not channel_id:
            if self._process:
                self._process(Message.NotificationType.ERROR, f"Error: Không tìm thấy Channel ID")
        else:
            if self._process:
                self._process(Message.NotificationType.NOTIFICATION, f"✅ ID kênh: {channel_id}")

            video_type = option_list_video["video_duration"]
            
            sort_by = option_list_video["video_sort"]
            type_craw = int(option_list_video["count"])

            count_video = 50  # Giá trị mặc định
            if type_craw < 0:
                count_video = 50

            # 🔹 Lấy danh sách video
            # video_type, sort_by, type_craw, count_video
            video_list = self.get_videos(channel_id, option)

            print(f"📌 Danh sách video: {video_list}")

            for video_id in tqdm(video_list, desc="Downloading videos", unit="video"):
                self.download_video_and_audio(video_id, '1080p')
                time.sleep(5)

     