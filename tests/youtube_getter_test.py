import pytest
from mmyoutube.youtube_getter import (
    random_get_video,
    get_video_match_today,
    get_videos_within_x_day,
    get_play_list,
)


class TestYouTubeGetter:
    @pytest.mark.slow
    def test_random_get_video(self):
        random_get_video()

    @pytest.mark.slow
    def test_get_video_match_today(self):
        get_video_match_today()

    @pytest.mark.slow
    def test_get_videos_within_x_day(self):
        get_videos_within_x_day()

    @pytest.mark.slow
    def test_get_play_list(self):
        get_play_list()
