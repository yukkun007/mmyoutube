import os
import httplib2
from pathlib import Path
from googleapiclient.discovery import build, Resource
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from dotenv import load_dotenv

YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"


# Google YouTube Data API リファレンス
# https://developers.google.com/youtube/v3/docs?hl=ja


def create_youtube() -> Resource:
    MISSING_CLIENT_SECRETS_MESSAGE = "missing client secrets."
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    flow = flow_from_clientsecrets(
        _create_client_secret(),
        message=MISSING_CLIENT_SECRETS_MESSAGE,
        scope=[YOUTUBE_READONLY_SCOPE, YOUTUBE_UPLOAD_SCOPE],
    )
    storage = Storage(_create_token())
    credentials: OAuth2Credentials = storage.get()
    # credentials: OAuth2Credentials = None

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)
        Path("mmyoutube_token_save.json").write_text(credentials.to_json())

    youtube: Resource = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()),
        # エラー回避: https://qiita.com/kai_kou/items/4b754c61ac225daa0f7d
        cache_discovery=False,
    )
    return youtube


def _create_client_secret() -> str:
    secret_path = "/tmp/mmyoutube_client_secret.json"
    with open(secret_path, "w") as st:
        load_dotenv(verbose=True)
        secret = os.environ.get("mmyoutube_client_secret_contents", "dummy")
        st.write(secret)
        st.close()
    return secret_path


def _create_token() -> str:
    oauth_path = "/tmp/mmyoutube_token.json"
    with open(oauth_path, "w") as oa:
        load_dotenv(verbose=True)
        contents = os.environ.get("mmyoutube_token_contents", "dummy")
        oa.write(contents)
        oa.close()
    return oauth_path


# トークン保存時に利用
# if __name__ == "__main__":
#     create_youtube()
