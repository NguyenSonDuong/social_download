from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from douyin.douyin_key import Option
import requests

class Douyin:
    _process = None
    def __init__(self, process, Option = Option()):
        self._process = process
        self.option = Option
        pass

    def get_video_source(self):
        # Lấy mã nguồn của trang
        page_source = self.get_page_source(self.option.video_url)
        
        # Sử dụng BeautifulSoup để phân tích cú pháp HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Tìm thẻ <video> và thẻ <source> bên trong nó
        video_tag = soup.find('video')
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and 'src' in source_tag.attrs:
                return source_tag['src']
        
        return None
    def get_page_source(self):
        # Đường dẫn đến ChromeDriver
        
        # Tùy chọn cho Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ headless (không hiển thị giao diện)
        
        # Khởi tạo trình điều khiển Chrome
        driver = webdriver.Chrome( options=chrome_options)
        
        # Mở URL
        driver.get(self.option.video_url)
        
        # Chờ đối tượng có id 'RENDER_DATA' xuất hiện
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "RENDER_DATA")))
        
        # Lấy mã nguồn của trang
        page_source = driver.page_source
        
        # Đóng trình duyệt
        driver.quit()
        
        return page_source

    def download_video(self,video_url):
        """
        Downloads the video from the given URL and saves it to the specified file.
        
        :param video_url: The URL of the video to download.
        :param file_name: The name of the file to save the video as.
        """
        response = requests.get(f"https:{video_url}", stream=True)
        if response.status_code == 200:
            with open(self.option.output_path+"/douyin.mp4", 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"Video downloaded successfully: {self.option.output_path+"/douyin.mp4"}")
        else:
            print(f"Failed to download video. Status code: {response.status_code}")


   