import pytest
from mmyoutube.video import Video


@pytest.fixture()
def video_1():
    playlist_item = {
        "snippet": {
            "title": "titleTest",
            "resourceId": {"videoId": "videoIdTest"},
            "thumbnails": {"high": {"url": "urlTest"}},
            "publishedAt": "publishedAtTest",
        }
    }
    video = Video(playlist_item)
    return video


@pytest.fixture()
def video_2():
    playlist_item = {
        "snippet": {
            "title": "2019/01/01 titleTest",
            "resourceId": {"videoId": "videoIdTest"},
            "thumbnails": {"high": {"url": "urlTest"}},
            "publishedAt": "publishedAtTest",
        }
    }
    video = Video(playlist_item)
    return video


@pytest.fixture()
def video_none():
    video = Video(None)
    return video


class TestVideo:
    def test_to_string(self, video_1: Video, video_2: Video, video_none: Video):
        video_1.to_string()
        video_2.to_string()
        video_none.to_string()
