import datetime
from typing import Dict


class Video:
    def __init__(self, playlist_item: Dict):
        try:
            self.title: str = playlist_item["snippet"]["title"]
            self.past_years: str = self._get_past_years(self.title[:4])
            self.video_id: str = playlist_item["snippet"]["resourceId"]["videoId"]
            self.url: str = playlist_item["snippet"]["thumbnails"]["high"]["url"]
            self.published_at: str = playlist_item["snippet"]["publishedAt"]
        except Exception:
            self.title: str = "none"
            self.past_years: str = "none"
            self.video_id: str = "none"
            self.url: str = "none"
            self.published_at: str = "none"

        print("create video object: \n" + self.to_string())

    def _get_past_years(self, year_str: str) -> str:
        try:
            now = datetime.datetime.now()
            return str(now.year - int(year_str))
        except ValueError:
            return "？"

    def to_string(self) -> str:
        string = """
        -------------------------------------------------------
        title:        {}
        video_id:     {}
        past_years:   {}
        url:          {}
        published_at: {}
        -------------------------------------------------------
        """.format(
            self.title, self.video_id, self.past_years, self.url, self.published_at
        )
        return string
