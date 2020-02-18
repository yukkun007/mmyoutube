import pytest
from mmyoutube.youtube_uploader import upload
from mmyoutube.upload_option import UploadOption


class TestYoutubeUploader:
    @pytest.mark.slow
    def test_upload(self):
        options = UploadOption(
            {
                "file": "./tests/data/test.mp4",
                "title": "hogehoge",
                "description": "これは説明です。",
                "keywords": "hoge,foo,bar",
            }
        )
        upload(options)
