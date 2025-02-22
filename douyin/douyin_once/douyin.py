import asyncio
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.dl import DouyinDownloader
from f2.utils.conf_manager import ConfigManager
from datetime import datetime
import os

class DouyinStatus:
    START = 0
    PROCESS = 1
    DONE = 2
    ERROR = -1
    DONE_ONE = 3
    DOUYIN_PROCESS = 4
    DOUYIN_DONE_ONCE = 5
    DOUYIN_DONE = 6
class Douyin:
    _processInfo = None
    _processDownload = None
    _processError = None
    
    def __init__(self, processInfo, processDownload, processError):
        self._processInfo = processInfo
        self._processDownload = processDownload
        self._processError = processError
        self.success = []
        self.error = []
        self.total_videos = 0
        self.isStopDownload = False

    async def getInfo(self, sec_user_id, count, from_date, to_date ):
        self._processInfo(0,DouyinStatus.START)
        kwargs = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
                "Referer": "https://www.douyin.com/",
            },
            "proxies": {"http://": None, "https://": None},
            "mode": "post",
            "media": "video"
        } | ConfigManager("douyin/douyin_once/conf/app.yaml").get_config("douyin")
        
        dyhandler = DouyinHandler(kwargs)
        
        i=0
        all_video = []
        try:
            async for aweme_list in dyhandler.fetch_user_post_videos(sec_user_id=sec_user_id):
                self._processInfo(len(all_video),DouyinStatus.START)
                if not aweme_list:
                    print(f"Không thể lấy thông tin video cho user: {sec_user_id}")
                    self._processError(f"Không thể lấy thông tin video cho user: {sec_user_id}",DouyinStatus.ERROR)
                    return None
                videos = [video for video in aweme_list._to_list() if video.get("aweme_type") == 0]
                if from_date and to_date:
                    for video in videos:
                        create_date =  datetime.strptime(video["create_time"], "%Y-%m-%d %H-%M-%S")
                        if from_date <= create_date <= to_date:
                            all_video.append(video)
                else:
                    all_video.extend(videos)
                self.total_videos = len(all_video)
                i = i+self.total_videos

                if i>= count and count >0:
                    all_video = all_video[0:count]
                    break
                print(f"Đã lấy video: {i}")
        except Exception as ex:
            self._processError(f"Lỗi khi lấy thông tin video cho user: {sec_user_id}",DouyinStatus.ERROR)
        self._processInfo(len(all_video),DouyinStatus.DONE)
        return all_video
    
    async def downloadVideo(self, videos, download_folder):
        kwargs = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
                "Referer": "https://www.douyin.com/",
            },
            "proxies": {"http://": None, "https://": None},
            "mode": "post",
        } | ConfigManager("douyin/douyin_once/conf/app.yaml").get_config("douyin")
        self._processDownload(len(videos),self.success,self.error,DouyinStatus.START)
        dowloader = DouyinDownloader(kwargs)
        for dem in range(0,len(videos),2):
            try:
                
                self._processDownload(len(videos),[videos[dem]],self.error,DouyinStatus.DOUYIN_PROCESS)
                await dowloader.create_download_tasks(
                    kwargs,[videos[dem],videos[dem+1]], download_folder
                )
                self._processDownload(len(videos),[videos[dem]],self.error,DouyinStatus.DOUYIN_DONE_ONCE)
                self.success.extend([videos[dem],videos[dem+1]])
            except Exception as ex:
                self.error.extend([videos[dem],videos[dem+1]])
            self._processDownload(len(videos),self.success,self.error,DouyinStatus.PROCESS)
            
    def run(self, sec_user_id,setting):
        dir_list = os.listdir(setting["folder_save_video"])
        from_date = None
        to_date = None
        if setting["order_download"] == "1":
            order = "date"
        elif setting["order_download"] == "2":
            order = "viewCount"
        elif setting["order_download"] == "3":
            order = "date"
        elif setting["order_download"] == "4":
            from_date = datetime.strptime(setting["from_time"], "%d/%m/%Y")
            to_date = datetime.strptime(setting["to_time"], "%d/%m/%Y")
        elif setting["order_download"] == "5":
            from_date = datetime.strptime(setting["from_time"], "%d/%m/%Y")
            to_date = datetime.strptime(setting["to_time"], "%d/%m/%Y")
        elif setting["order_download"] == "6":
            from_date = datetime.strptime(setting["from_time"], "%d/%m/%Y")
            to_date = datetime.strptime(setting["to_time"], "%d/%m/%Y")

        count = -1
        if setting["count_download"] != None and setting["count_download"] != "" :
            count = int(setting["count_download"])

        result = asyncio.run(self.getInfo(sec_user_id,count,from_date,to_date))
        if len(result) <=0:
            self._processDownload(0,self.success,self.error,DouyinStatus.DONE)
            return False
        asyncio.run(self.downloadVideo(result,setting["folder_save_video"]))
        self._processDownload(0,self.success,self.error,DouyinStatus.DONE)

    
