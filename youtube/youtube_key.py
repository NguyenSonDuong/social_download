from enum import Enum
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
