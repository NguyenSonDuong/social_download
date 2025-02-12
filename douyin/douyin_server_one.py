from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from douyin.douyin_key import Option
import re
from message.message import Message
import requests
import time
import os
class Douyin:
    _process = None

    def __init__(self, process, Option = Option()):
        self._process = process
        self.option = Option
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome( options=chrome_options)

    def clean_chinese_text(self,text):
        cleaned_text = re.sub(r"[^\u4e00-\u9fff]", "", text)
        return cleaned_text
    
    def get_page_sources(self):
        if self._process:
            self._process(Message.NotificationType.NOTIFICATION, f"{Message.Douyin.message_get_info_channel_start_browser}")
        error_get_link = []
        urls = []
        for url in self.option.video_url:
            if self._process:
                self._process(Message.NotificationType.NOTIFICATION, f"{Message.Douyin.message_get_info_channel_process_url}")
            try:
                self.driver.get(url)
                time.sleep(10)
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
                            "title": title.string
                        })
            except Exception as ex:
                if self._process:
                    self._process(Message.NotificationType.ERROR, f"{Message.Douyin.message_get_info_channel_error_url}")
                error_get_link(url)
        self.driver.quit()
        if self._process:
                self._process(Message.NotificationType.NOTIFICATION, f"{Message.Douyin.message_get_info_channel_process_url}")
        return urls , error_get_link

    def download_video(self,video_urls):
        
        for url in video_urls:
            filename = f"{self.option.output_path}/{self.clean_chinese_text(url["title"])}.mp4"
            if self._process:
                self._process(Message.NotificationType.NOTIFICATION, f"{Message.Douyin.message_get_info_channel_start_download}: {filename}")
            if not os.path.exists(self.option.output_path):
                os.makedirs(self.option.output_path)
            response = requests.get(f"https:{url["url"]}")
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                if self._process:
                    self._process(Message.NotificationType.NOTIFICATION, f"{Message.Douyin.message_get_info_channel_success_download}: {filename}")
            else:
                if self._process:
                    self._process(Message.NotificationType.ERROR, f"{Message.Douyin.message_get_info_channel_error_download}: {filename} | {response.status_code}")
                


   