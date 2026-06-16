import asyncio
import re
from typing import Tuple, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from src.models.interfaces import IVideoSearcher

class BrowserConfig:
    """負責管理與封裝 WebDriver 的設定"""
    @staticmethod
    def get_chrome_options() -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options

    @staticmethod
    def create_driver() -> webdriver.Chrome:
        services = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=services, options=BrowserConfig.get_chrome_options())


class YouTubeCrawler(IVideoSearcher):
    """實作 IVideoSearcher 介面的 YouTube 爬蟲服務"""
    
    SEARCH_URL_TEMPLATE = 'https://www.youtube.com/results?search_query={}'

    def __init__(self):
        self.driver = None

    def _ensure_driver(self):
        """確保 driver 存在且可用"""
        try:
            if self.driver is None:
                self.driver = BrowserConfig.create_driver()
            else:
                # 測試 driver
                _ = self.driver.title
        except Exception:
            # 如果拋出例外 (例如 WebDriverException)，代表連線已斷開，需重新初始化
            self.driver = BrowserConfig.create_driver()

    def _wait_for_page_load(self, timeout: int = 5):
        """等待網頁的 DOM 樹載入完成"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    # 將原本會卡死系統的 Selenium 邏輯改為同步的內部方法
    def _search_sync(self, keyword: str) -> Tuple[List[str], List[str]]:
        self._ensure_driver()
        formatted_keyword = keyword.replace(' ', '+').strip()
        url = self.SEARCH_URL_TEMPLATE.format(formatted_keyword)
        
        song_names = []
        song_urls = []

        try:
            self.driver.get(url)
            self._wait_for_page_load()
            videos = self.driver.find_elements(By.CSS_SELECTOR, 'a#video-title')
            for video in videos:
                self.driver.execute_script("arguments[0].scrollIntoView();", video)
                title = video.get_attribute('title')
                raw_link = video.get_attribute('href')
                
                if title and raw_link:
                    song_names.append(title)
                    song_urls.append(re.sub(r'(&.+)$', '', raw_link))
        except Exception as e:
            print(f"[爬蟲錯誤] 搜尋影片失敗: {e}")
            
        return song_names, song_urls

    # 實作介面定義的非同步方法
    async def search_videos(self, keyword: str) -> Tuple[List[str], List[str]]:
        """透過背景執行緒運行 Selenium，保護機器人的語音流暢度"""
        return await asyncio.to_thread(self._search_sync, keyword)

    def close(self):
        """釋放 driver 資源"""
        if self.driver:
            self.driver.quit()
            self.driver = None