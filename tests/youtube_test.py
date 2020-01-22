import pytest
import mmyoutube.youtube as youtube


class TestYouTube:
    @pytest.mark.slow
    def test_random_get_video(self):
        youtube.random_get_video()

    @pytest.mark.slow
    def test_get_video_match_today(self):
        youtube.get_video_match_today()

    @pytest.mark.slow
    def test_get_videos_within_x_day(self):
        youtube.get_videos_within_x_day()
