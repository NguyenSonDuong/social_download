import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import time
import random
API_KEY = "AIzaSyC6XAJGYvbDHiLYFGpv8BpUz9PRSNwIQEA"
def GetInfoChannel(url, order, from_date, to_date,nextpagetoken):

    if is_valid_youtube_handle(url):
        CHANNEL_ID = GetIdChannel(url)
    else:
        CHANNEL_ID = extract_channel_id(url)

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
        "key": API_KEY
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
            filtered_videos.append((video_id,title, kind, video_url, publish_datetime.strftime(r"%Y-%m-%d")))
    nextpagetoken = data.get("nextPageToken")
    if nextpagetoken:
        return filtered_videos, nextpagetoken
    else:
        return filtered_videos, None

def getTotalVideoChannel():
    url = "https://www.youtube.com/@H2ORemix88"
    if is_valid_youtube_handle(url):
        CHANNEL_ID = GetIdChannel(url)
    else:
        CHANNEL_ID = extract_channel_id(url)
# API Endpoint
    url = "https://www.googleapis.com/youtube/v3/channels"

    # Gửi request để lấy số lượng video
    params = {
        "part": "statistics",
        "id": CHANNEL_ID,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

# Lấy tổng số video
    if "items" in data and len(data["items"]) > 0:
        video_count = data["items"][0]["statistics"]["videoCount"]
        print(f"Tổng số video trên kênh: {video_count}")
    else:
        print("Không tìm thấy thông tin kênh!")

def GetIdChannel(url):
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
        # print(f"Href: {href_value}")
    else:
        print("Không tìm thấy thẻ <link> phù hợp!")
        return ""
    
def is_valid_youtube_handle(url):
    # Regex để kiểm tra định dạng https://www.youtube.com/@handle
    pattern = r"^https://www\.youtube\.com/@[\w\d_-]+$"
    
    # Kiểm tra URL
    return bool(re.match(pattern, url))

def extract_channel_id(url):
    pattern = r"https://www\.youtube\.com/channel/([\w-]+)"
    match = re.search(pattern, url)
    return match.group(1) if match else None


# # 
# stop = False
# to_time = datetime.now()
# from_time = datetime(1990, 1, 1)
# nextpagetoken = None
# while not stop:
#     filtered_videos, nextpagetoken = GetInfoChannel("https://www.youtube.com/@H2ORemix88","date",from_time,to_time,nextpagetoken)
#     print(filtered_videos)
#     time.sleep(random.randint(0,3))
#     print("Page next=============================================================>")

getTotalVideoChannel()