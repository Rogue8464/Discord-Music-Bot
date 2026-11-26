import asyncio
import yt_dlp as youtube_dl
from .interfaces import IAudioExtractor
from .domain import Song
from src.crawl import YouTubeCrawler
from typing import Optional

class YTDLPExtractor(IAudioExtractor):
    def __init__(self):
        self.options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'socket_timeout': 10,  # 增加超時時間
            'retries': 5,          # 遇到網路波動時自動重試
            # 絕對不要加 'source_address': '0.0.0.0'，讓 OS 自動決定最佳網卡路由
            'extractor_retries': 3 # 針對擷取 API 的重試
        }
        self.crawler = YouTubeCrawler()

    @staticmethod
    def _pick_audio_url(info: dict) -> Optional[str]:
        """從 yt-dlp 解析結果中優先取得最佳純音訊串流網址。"""
        if info.get('url'):
            return info['url']

        requested = info.get('requested_formats') or []
        for fmt in requested:
            if fmt.get('acodec') != 'none' and fmt.get('url'):
                return fmt['url']

        formats = info.get('formats') or []
        audio_only = next(
            (f['url'] for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('url')),
            None,
        )
        if audio_only:
            return audio_only

        return next(
            (f['url'] for f in formats if f.get('acodec') != 'none' and f.get('url')),
            None,
        )

    # 同步且會阻塞的耗時邏輯
    def _extract_sync(self, url: str) -> Optional[Song]:
        with youtube_dl.YoutubeDL(self.options) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None
                audio_url = self._pick_audio_url(info)
                if audio_url:
                    return Song(url=url, title=info.get('title', '未知標題'), stream_url=audio_url, info=info)
            except Exception as e:
                print(f"解析失敗: {e}")
        return None

    async def extract_info(self, url: str) -> Optional[Song]:
        """
        利用 asyncio.to_thread 將耗時的 yt-dlp 操作丟到背景執行緒。
        這樣主事件迴圈 (Event Loop) 就能繼續順暢地推送 Discord 語音封包。
        """
        return await asyncio.to_thread(self._extract_sync, url)