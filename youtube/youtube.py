import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import time
import random
import yt_dlp
from pytube import YouTube
class YoutubeStatus:
    START = 0
    PROCESS = 1
    DONE = 2
    ERROR = -1
    DONE_ONE = 3

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

    def GetInfoChannel(self, url, order, from_date, to_date,nextpagetoken):
        try:
            
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
            try:    
                response = requests.get(base_url, params=params)
                data = response.json()
            except Exception as ex:
                self._processError("Lỗi tải dữ liệu! kiểm tra lại kết nối Internet", YoutubeStatus.ERROR)
                return None
            filtered_videos = []
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                kind = item["id"]["kind"]
                publish_date = item["snippet"]["publishedAt"]
                publish_datetime = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
                if from_date and to_date:
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
                else:
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
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)
    
    def GetIdChannel(self,url):
        try:
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
                    self._processError("Không tìm thấy Channel ID!", YoutubeStatus.ERROR)
                    return None
            else:
                self._processError("Không tìm thấy thẻ <link> phù hợp!", YoutubeStatus.ERROR)
                return None
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)
        
    def is_valid_youtube_handle(self,url):
        pattern = r"^https://www\.youtube\.com/@[\w\d_-]+$"
        return bool(re.match(pattern, url))

    def extract_channel_id(self ,url):
        try:
            pattern = r"https://www\.youtube\.com/channel/([\w-]+)"
            match = re.search(pattern, url)
            return match.group(1) if match else None
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)
            return None

    def getTotalVideoChannel(self,url):
        try:
            if self.is_valid_youtube_handle(url):
                CHANNEL_ID = self.GetIdChannel(url)
            else:
                CHANNEL_ID = self.extract_channel_id(url)

            url = "https://www.googleapis.com/youtube/v3/channels"
            if not CHANNEL_ID:
                self._processError("Không tìm thấy channel id", YoutubeStatus.ERROR)
                return -1
            
            params = {
                "part": "statistics",
                "id": CHANNEL_ID,
                "key": self.API_KEY
            }
            try:
                response = requests.get(url, params=params)
                data = response.json()
            except Exception as ex:
                self._processError(str(ex), YoutubeStatus.ERROR)
                return -1

            if "items" in data and len(data["items"]) > 0:
                video_count = data["items"][0]["statistics"]["videoCount"]
                print(f"Tổng số video trên kênh: {video_count}")
                return int(video_count)
            else:
                self._processError("Không tìm thấy thông tin kênh!", YoutubeStatus.ERROR)
                return -1
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)
        
    def download_video(self, video,download_folder):
        filename = self.sanitize_filename(video["title"])
        if not filename:
            filename = f"filename_{datetime.datetime.now().timestamp()}"
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
            except Exception as ex:
                self._processError(str(ex), YoutubeStatus.ERROR)
                self._processError("Đang bắt đầu thử tải lại ... ", YoutubeStatus.START)
                try:
                    self.dowload_Video_2(video,download_folder)
                    return True
                except Exception as ex:
                    self._processError(str(ex), YoutubeStatus.ERROR)
                    return False
        
    def dowload_Video_2(self, video,download_folder):
        filename = self.sanitize_filename(video["title"])   
        if not filename:
            filename = f"filename_{datetime.datetime.now().timestamp()}"
        yt = YouTube(video["video_url"], on_progress_callback=self.progress_callback)

        stream = yt.streams.get_highest_resolution()

        stream.download(output_path=download_folder)

        print("Tải video thành công!")
    def sanitize_filename(self,title, replacement="-"):
        try:
            sanitized = re.sub(r'[^\w\sÀ-ỹ]', '', title)
            sanitized = re.sub(r'\s+', '-', sanitized).strip('-')
            return sanitized    
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)
            return None

    def _download_hook(self,d):
        try:
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
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)
    def progress_callback(self,stream, chunk, bytes_remaining):
        try:
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percent = (bytes_downloaded / total_size) * 100
            self._processDownloadVideo(percent,0,0, 0, YoutubeStatus.PROCESS)
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)

    def run(self, url,count, order, from_date, to_date, download_folder):
        try:
            stop = False
            nextpagetoken = None
            videos = []
            self._processInfo(len(videos),YoutubeStatus.START)

            if order == "old":
                from_date = None
                to_date = None

            while not stop:
                filtered_videos, nextpagetoken = self.GetInfoChannel(url,"viewCount" if order == "viewCount" else "date", from_date, to_date , nextpagetoken)
                videos.extend(filtered_videos)
                if len(videos) >= count and order != "old":
                    break
                self._processInfo(len(videos),YoutubeStatus.PROCESS)
                time.sleep(random.randint(0,2))
                if not nextpagetoken:
                    stop = True

            if order == "old" and count>0:
                videos = videos[-count:]
            elif order == "old" and count<0:
                videos = videos[::-1]

            self._processInfo(len(videos),YoutubeStatus.DONE)

            videoDownload = []
            videoError = []


            if count <0:
                videos = videos
            else:
                videos = videos[0:count]
                
            for video in videos:
                self._processDownload(len(videos),videoDownload,videoError,YoutubeStatus.START)
                self._processDownload(len(videos),videoDownload,videoError,YoutubeStatus.PROCESS)
                status = self.download_video(video,download_folder)
                if status:
                    videoDownload.append(video)
                    self._processDownload(len(videos),[video],[],YoutubeStatus.DONE_ONE)
                else:
                    videoError.append(video)
                    self._processDownload(len(videos),videoDownload,video,YoutubeStatus.ERROR)
            self._processDownload(len(videos),videoDownload,videoError,YoutubeStatus.DONE)
        except Exception as ex:
            self._processError(str(ex), YoutubeStatus.ERROR)

        