import pytest
from mmyoutube.youtube_updater import add_to_play_list, delete_from_play_list


class TestYoutubeUpdater:
    @pytest.mark.slow
    def test_add_to_play_list(self):
        item_id = add_to_play_list("PLfZruavKtKZy0JdMo7PnbHAEo32twXVZl", "bRGeqa3ISEE")
        # すぐ削除
        delete_from_play_list(item_id)
