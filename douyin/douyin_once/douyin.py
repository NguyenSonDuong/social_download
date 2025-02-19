import asyncio
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.dl import DouyinDownloader
from f2.utils.conf_manager import ConfigManager
from datetime import datetime
class DouyinStatus:
    START = 0
    PROCESS = 1
    DONE = 2
    ERROR = -1
    DONE_ONE = 3
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
                    return
                # videos = aweme_list._to_list()
                videos = [video for video in aweme_list._to_list() if video.get("aweme_type") == 0]
                if from_date and to_date:
                    for video in videos:
                        create_date =  datetime.strptime(video["create_time"], "%Y-%m-%d %H-%M-%S")
                        if from_date <= create_date <= to_date:
                            all_video.append(video)
                else:
                    all_video.extend(video)
                self.total_videos = len(all_video)
                i = i+self.total_videos

                if i>= count and count >0:
                    all_video = all_video[0:count]
                    break
                print(f"Đã lấy video: {i}")
        except Exception as ex:
            print(ex)
        
        print("Tải video hoàn tất!")
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

        for video in videos:
            
            try:
                await dowloader.create_download_tasks(
                    kwargs,[video], download_folder
                )
                self.success.append(video)
            except Exception as ex:
                self.error.append(video)
            self._processDownload(len(videos),self.success,self.error,DouyinStatus.PROCESS)
            
    def run(self, sec_user_id, count, from_date, to_date,download_folder):
        
        result = asyncio.run(self.getInfo(sec_user_id,count,from_date,to_date))
        if len(result) <=0:
            self._processDownload(0,self.success,self.error,DouyinStatus.DONE)
            return False
        asyncio.run(self.downloadVideo(result,download_folder))
        self._processDownload(0,self.success,self.error,DouyinStatus.DONE)
        
# Thay thế 'sec_user_id' bằng ID người dùng cụ thể
# 
