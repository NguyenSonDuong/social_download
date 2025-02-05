from enum import Enum
from youtube_key import YoutubeKey
class Option:
    def __init__(self):

        self.channel_url = ""
        self.video_type= YoutubeKey.VideoType.VIDEO
        self.video_sort= YoutubeKey.VideoSort.PHOBIEN
        self.video_duration= YoutubeKey.VideoDuaration.ALLVIDEO
        self.video_quatity= YoutubeKey.VideoQuality.VideoFormat[0]
        self.output_path = "Downloads"
        self.count= -1

        pass

class YoutubeKey:
    
    class VideoDuaration:
        ALLVIDEO = 1
        VIDEODURATION_20MINUTE = 2
        VIDEODURATION_FROM4TO20MINUTE  = 3 
        VIDEODURATION_FROM1TO4MINUTE = 4
        VIDEODURATION_UNDER1MINUTE = 5
    class VideoSort:
        PHOBIEN = 1
        MOINHAT = 2
        CUNHAT = 3
    class VideoType:
        VIDEO = 1
        SHORT = 2

    class VideoQuality:
        VideoFormat = ["bestvideo+bestaudio"
               ,"worst"
               ,"bestvideo"
               ,"bestaudio"
               ,"worstvideo"
               ,"worstaudio"]
