import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Google YouTube Data API リファレンス
# https://developers.google.com/youtube/v3/docs?hl=ja


class Youtube:
    # APIのURLやスコープ
    api_url = {
        "playlistItems": "https://www.googleapis.com/youtube/v3/playlistItems",
        "playlists": "https://www.googleapis.com/youtube/v3/playlists",
    }
    scope = ["https://www.googleapis.com/auth/youtube"]

    def __init__(
        self,
        token_path: str = "/tmp/mmyoutube_new_token.json",
        credential_path: str = "/tmp/mmyoutube_client_secret.json",
        dotenv_path: str = None,
    ):
        load_dotenv(dotenv_path=dotenv_path, verbose=True)

        self._token_path: str = token_path
        self._credential_path: str = credential_path
        self._google_session: OAuth2Session = None
        self._google_session, logged_in = self._login()
        # ログイン処理が行われていたらトークンを保存
        # 本来自動保存だが動かないので追加
        if logged_in:
            self._save_token()
        # 有効期限の過ぎたトークンをリフレッシュ
        self._token_expires_at = datetime.fromtimestamp(
            self._google_session.token.get("expires_at")
        )
        self._check_and_refresh_token()

    # ログイン後に取得したトークンをjsonに保存
    def _save_token(self):
        logger.debug("トークンを保存しています")
        Path(self._token_path).write_text(json.dumps(self._google_session.token))

    # jsonが存在したら読み込み
    def _load_token(self):
        # 存在しない場合は期限切れのダミーを返す
        token = {
            "access_token": "",
            "refresh_token": "",
            "token_type": "",
            "expires_in": "-30",
            "expires_at": (datetime.now() - timedelta(hours=2)).timestamp(),
        }

        path = Path(self._token_path)

        if "mmyoutube_new_token_contents" in os.environ:
            # .envから読み込む
            token = json.loads(os.environ["mmyoutube_new_token_contents"])
        elif path.exists():
            logger.debug("トークンをファイルから読み込んでいます")
            token = json.loads(path.read_text())
        return token

    def _check_and_refresh_token(self):
        if datetime.now() + timedelta(minutes=10) > self._token_expires_at:
            logger.debug("トークンの期限切れが近いため、更新を行います")
            new_token = self._google_session.refresh_token(
                self._google_session.auto_refresh_url, **self._google_session.auto_refresh_kwargs
            )
            self._google_session.token = new_token
            self._token_expires_at = datetime.fromtimestamp(
                self._google_session.token.get("expires_at")
            )

    def _save_credential_from_env(self):
        logger.debug("認証情報を保存しています")
        credential = os.environ.get("mmyoutube_client_secret_contents", "dummy")
        Path(self._credential_path).write_text(credential)

    # ログインしてセッションオブジェクトを返す
    def _login(self):
        # 認証情報を環境変数から書き込み
        self._save_credential_from_env()
        # 認証情報を読み込み
        auth_info = json.loads(Path(self._credential_path).read_text()).get("installed", None)
        assert auth_info is not None
        # トークン読み込み
        token = self._load_token()
        # トークン更新用の認証情報
        extras = {
            "client_id": auth_info.get("client_id"),
            "client_secret": auth_info.get("client_secret"),
        }
        # セッションオブジェクトを作成
        # TODO: token_updaterの引数がたぶん合わない
        google_session = OAuth2Session(
            auth_info.get("client_id"),
            scope=Youtube.scope,
            token=token,
            auto_refresh_kwargs=extras,
            token_updater=self._save_token,
            auto_refresh_url=auth_info.get("token_uri"),
            redirect_uri=auth_info.get("redirect_uris")[0],
        )
        # ログインしていない場合ログインを行う
        logged_in = False
        if not google_session.authorized:
            logger.debug("ログインを行います")
            authorization_url, state = google_session.authorization_url(
                auth_info.get("auth_uri"), access_type="offline", prompt="select_account"
            )
            # 認証URLにアクセスしてコードをペースト
            print("Access {} and paste code.".format(authorization_url))
            access_code = input(">>> ")
            google_session.fetch_token(
                auth_info.get("token_uri"),
                client_secret=auth_info.get("client_secret"),
                code=access_code,
            )
            assert google_session.authorized
            logged_in = True
        return google_session, logged_in

    def get(self, *args, **kwargs):
        self._check_and_refresh_token()
        return self._google_session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self._check_and_refresh_token()
        return self._google_session.post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._check_and_refresh_token()
        return self._google_session.delete(*args, **kwargs)
