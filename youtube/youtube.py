import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import time
import random
import yt_dlp

class YoutubeStatus:
    START = 0
    PROCESS = 1
    DONE = 2
    ERROR = -1

class Youtube:

    _processInfo = None
    _processDownload = None
    _processError = None
    _processDownloadVideo = None
    def __init__(self, processInfo, processDownload, processError, processDownloadVideo, API_KEY = "AIzaSyC6XAJGYvbDHiLYFGpv8BpUz9PRSNwIQEA" ):
        self.API_KEY = API_KEY
        self._processInfo = processInfo
        self._processDownload = processDownload
        self._processError = processError
        self._processDownloadVideo = processDownloadVideo

    def GetInfoChannel(self, url,count, order, from_date, to_date,nextpagetoken):

        if self.is_valid_youtube_handle(url):
            CHANNEL_ID = self.GetIdChannel(url)
        else:
            CHANNEL_ID = self.extract_channel_id(url)

        if not CHANNEL_ID or CHANNEL_ID == "":
            print("Không lấy được ID Youtube")

        # API Endpoint để lấy video từ kênh
        base_url = "https://www.googleapis.com/youtube/v3/search"

        params = {
            "part": "snippet",
            "channelId": CHANNEL_ID,
            "order": order,
            "maxResults": 50,  # Số lượng video tối đa mỗi lần gọi API
            "type": "video",
            "key": self.API_KEY
        }
        if nextpagetoken:
            params["pageToken"] = nextpagetoken
        # Gửi yêu cầu API để lấy danh sách video
        response = requests.get(base_url, params=params)
        data = response.json()
        
        filtered_videos = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            kind = item["id"]["kind"]
            publish_date = item["snippet"]["publishedAt"]
            publish_datetime = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
            
            # Kiểm tra nếu video nằm trong khoảng thời gian mong muốn
            if from_date <= publish_datetime <= to_date:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                filtered_videos.append({
                    "video_id":video_id,
                    "title":title, 
                    "kind":kind, 
                    "video_url":video_url, 
                    "publish_date": publish_datetime.strftime(r"%Y-%m-%d")
                })
        nextpagetoken = data.get("nextPageToken")
        if nextpagetoken:
            return filtered_videos, nextpagetoken
        else:
            return filtered_videos, None
    
    def GetIdChannel(self,url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        meta_tag = soup.find("meta", {"property": "al:ios:url"})
        if meta_tag:
            href_value = meta_tag.get("content")
            pattern = r"www\.youtube\.com/channel/([\w-]+)"
            match = re.search(pattern, href_value)

            if match:
                channel_id = match.group(1)
                print(f"Channel ID: {channel_id}")
                return channel_id
            else:
                print("Không tìm thấy Channel ID!")
                return ""
        else:
            print("Không tìm thấy thẻ <link> phù hợp!")
            return ""
        
    def is_valid_youtube_handle(self,url):
        pattern = r"^https://www\.youtube\.com/@[\w\d_-]+$"
        return bool(re.match(pattern, url))

    def extract_channel_id(self ,url):
        pattern = r"https://www\.youtube\.com/channel/([\w-]+)"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def getTotalVideoChannel(self,url):
        if self.is_valid_youtube_handle(url):
            CHANNEL_ID = self.GetIdChannel(url)
        else:
            CHANNEL_ID = self.extract_channel_id(url)
    # API Endpoint
        url = "https://www.googleapis.com/youtube/v3/channels"

        # Gửi request để lấy số lượng video
        params = {
            "part": "statistics",
            "id": CHANNEL_ID,
            "key": self.API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

    # Lấy tổng số video
        if "items" in data and len(data["items"]) > 0:
            video_count = data["items"][0]["statistics"]["videoCount"]
            print(f"Tổng số video trên kênh: {video_count}")
            return int(video_count)
        else:
            print("Không tìm thấy thông tin kênh!")
            return -1
    
    def download_video(self, video,download_folder):
        filename = self.sanitize_filename(video["title"])
        ydl_opts = {
            'format': "bestvideo+bestaudio",  
            'outtmpl': f'{download_folder}/{filename}.%(ext)s',
            'progress_hooks': [self._download_hook],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([video["video_url"]]) 
                return True
            except Exception as e:
                return False
    def sanitize_filename(self,title, replacement="-"):
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        sanitized = re.sub(r'\s+', replacement, sanitized)  
        sanitized = re.sub(r'[^a-zA-Z0-9_.-]', replacement, sanitized)  
        sanitized = re.sub(r'[-_]+', replacement, sanitized).strip(replacement)
        return sanitized    


    def parse_size(self,size_str):
        if not size_str:
            return 0.0
        size_str = size_str.upper()
        units = {"B": 1, "KIB": 1024, "MIB": 1024**2, "GIB": 1024**3}
        for unit in units:
            if unit in size_str:
                return float(size_str.replace(unit, "").strip()) * units[unit] / (1024**2)
        return float(size_str)
    def _download_hook(self,d):
        if d['status'] == 'downloading':
            if "total_bytes" not in d or "downloaded_bytes" not in d:
                percent = float(d['downloaded_bytes']/d["total_bytes_estimate"])*100  
            else:
                percent = float(d['downloaded_bytes']/d["total_bytes"])*100  
            speed = 0.0 
            downloaded = 0.0
            total = 0.0
            self._processDownloadVideo(percent,speed,downloaded, total, YoutubeStatus.PROCESS)
        elif d['status'] == 'finished':
            self._processDownloadVideo(0,0,0, 0, YoutubeStatus.DONE)
        elif d['status'] == 'error':
            self._processDownloadVideo(-1,-1,-1,-1, YoutubeStatus.DONE)

    def run(self, url,count, order, from_date, to_date, download_folder):
        stop = False
        nextpagetoken = None
        videos = []
        self._processInfo(len(videos),YoutubeStatus.START)
        while not stop:
            filtered_videos, nextpagetoken = self.GetInfoChannel(url, count,order, from_date, to_date , nextpagetoken)
            videos.extend(filtered_videos)
            if len(videos) >= count:
                break
            self._processInfo(len(videos),YoutubeStatus.PROCESS)
            print(filtered_videos)
            time.sleep(random.randint(0,3))
            if not nextpagetoken:
                stop = True
        self._processInfo(len(videos),YoutubeStatus.DONE)
        videoDownload = []
        videoError = []
        self._processDownload(videoDownload,videoError,YoutubeStatus.START)
        for step in range(0,count):
            status = self.download_video(videos[step],download_folder)
            if status:
                videoDownload.append(videos[step])
            else:
                videoError.append(videos[step])
                self._processDownload(videoDownload,[videos[step]],YoutubeStatus.ERROR)
            self._processDownload(videoDownload,videoError,YoutubeStatus.PROCESS)
        self._processDownload(videoDownload,videoError,YoutubeStatus.DONE)

        