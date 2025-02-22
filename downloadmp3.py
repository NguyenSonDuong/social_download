import yt_dlp
from datetime import  datetime

def download_video(type,video,download_folder):
        filename = f"filename_{datetime.now().timestamp()}"
        ydl_opts = {
            'format': "bestvideo" if type == "1" else "bestaudio" if type=="2" else "best",
            'outtmpl': f'{download_folder}/{filename}.%(ext)s',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([video])
                return True
            except Exception as ex:
                print(ex)

download_video(input("Nhập loại: "),input("Nhập url: "),input("Nhập thư mục lưu: "))