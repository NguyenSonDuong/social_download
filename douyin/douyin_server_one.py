from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from douyin.douyin_key import Option
import re
import requests

class Douyin:
    _process = None

    def __init__(self, process, Option = Option()):
        self._process = process
        self.option = Option
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome( options=chrome_options)

    def clean_chinese_text(text):
        cleaned_text = re.sub(r"[^\u4e00-\u9fff]", "", text)
        return cleaned_text
    
    def get_page_sources(self):

        urls = []
        for url in self.option.video_url:
            self.driver =  self.driver.get(url)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "RENDER_DATA")))
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            video_tag = soup.find('video')
            title = soup.find('title')
            if video_tag:
                source_tag = video_tag.find('source')
                if source_tag and 'src' in source_tag.attrs:
                    # urls.append()
                    urls.append({
                        "url": source_tag['src'],
                        "title": title
                    })
        self.driver.quit()
        return urls

    def download_video(self,video_urls):
        for url in video_urls:
            filename = f"{self.option.output_path}/{self.clean_chinese_text(url["title"])}.mp4"
            response = requests.get(f"https:{url["url"]}")
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                print(f"Video downloaded successfully: {filename}")
            else:
                print(f"Failed to download video. Status code: {response.status_code}")


   