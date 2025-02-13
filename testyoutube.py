import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
API_KEY = "AIzaSyC6XAJGYvbDHiLYFGpv8BpUz9PRSNwIQEA"
def GetInfoChannel(url):

    # ID của kênh YouTube (Thay bằng ID kênh)
    CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # Ví dụ: Channel Google Developers
    if is_valid_youtube_handle(url):
        CHANNEL_ID = GetIdChannel(url)
    else:
        CHANNEL_ID = extract_channel_id(url)

    if not CHANNEL_ID or CHANNEL_ID == "":
        print("Không lấy được ID Youtube")

    
    # Khoảng thời gian cần lọc
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 2, 10)

    # API Endpoint để lấy video từ kênh
    base_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "channelId": CHANNEL_ID,
        "order": "date",
        "maxResults": 50,  # Số lượng video tối đa mỗi lần gọi API
        "type": "video",
        "key": API_KEY
    }

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
            filtered_videos.append((title, kind, video_url, publish_datetime.strftime(r"%Y-%m-%d")))

    print(f"Có {len(filtered_videos)} video trong khoảng thời gian từ {from_date.date()} đến {to_date.date()}:")
    for idx, (title, url, date) in enumerate(filtered_videos, start=1):
        print(f"{idx}. {title} - {url} - Đăng ngày {date}")

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


GetInfoChannel("https://www.youtube.com/@nguyenthuongofficial7353")