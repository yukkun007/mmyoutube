import os
import random
import re
import httplib2
from typing import List, Union, Dict, Callable
from datetime import datetime, timedelta
from apiclient.discovery import build, Resource
from apiclient.http import HttpRequest
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from dotenv import load_dotenv

from mmyoutube.video import Video


def random_get_video() -> Union[None, Video]:
    return _get_video(_filter_none)


def _filter_none(items: List[Dict]) -> List[Dict]:
    return items


def get_video_match_today() -> Union[None, Video]:
    return _get_video(_filter_match_today)


def _filter_match_today(items: List[Dict]) -> List[Dict]:
    return list(filter(lambda item: _is_match_today(item["snippet"]["title"]), items))


def _is_match_today(content: str) -> bool:
    pattern = re.compile(r"^2\d{3}" + datetime.now().strftime("/%m/%d"))
    if re.search(pattern, content):
        print("matched video title on today! content=" + content)
        return True
    else:
        return False


def get_videos_within_x_day(x: float = 7) -> List[Video]:
    return _get_videos(_filter_within_x_day, {"within_x_day": x})


def _filter_within_x_day(items: List[Dict], x: float) -> List[Dict]:
    return list(filter(lambda item: _is_within_x_day(item["snippet"]["publishedAt"], x), items))


def _is_within_x_day(date_str: str, x: float) -> bool:
    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.000Z")
    now = datetime.now()
    one_week_ago = now - timedelta(days=x)
    if one_week_ago < date:
        # １週間以内ならtrue
        return True
    else:
        return False


def _get_video(filter_method: Callable[[List[Dict]], List[Dict]]) -> Union[None, Video]:
    youtube = _create_youtube()

    playlistitems_list_request = _get_playlistitems_list_request(youtube)

    # playlist itemはいっぺんに取れないので下記のようにwhileで回す必要がある
    tmp_choiced_items: List[Dict] = []
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        playlist_items: List[Dict] = playlistitems_list_response["items"]
        filterd_playlist_items = filter_method(playlist_items)
        choiced_playlist_item = _choice_playlist_item(filterd_playlist_items)
        # choiceしたitemをtmpにためておく
        if choiced_playlist_item is not None:
            tmp_choiced_items.append(choiced_playlist_item)

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response
        )

    # 最後にもう一度選択
    return Video(_choice_playlist_item(tmp_choiced_items))


def _get_videos(
    filter_method: Callable[[List[Dict], float], List[Dict]], param: Dict
) -> List[Video]:
    youtube = _create_youtube()

    playlistitems_list_request = _get_playlistitems_list_request(youtube)

    all_items: List[Dict] = []
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        items: List[Dict] = playlistitems_list_response["items"]
        filterd_items = filter_method(items, param["within_x_day"])
        all_items.extend(filterd_items)

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response
        )

    print("found recent upload videos. count={}".format(len(all_items)))
    all_videos: List[Video] = []
    for item in all_items:
        all_videos.append(Video(item))

    # 最大でも１０個まで
    return all_videos[:10]


def _get_playlistitems_list_request(youtube: Resource) -> HttpRequest:
    channels_response = youtube.channels().list(mine=True, part="contentDetails").execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        print("scan all list(id:{}) item. start.....".format(uploads_list_id))

    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_list_id, part="snippet", maxResults=50
    )

    return playlistitems_list_request


def _choice_playlist_item(playlist_items: List[Dict]) -> Union[None, Dict]:
    items_number = len(playlist_items)
    if items_number > 0:
        index = random.randint(0, items_number - 1)
        print("video choice done. choiced_index={} from {}videos.".format(index, items_number))
        return playlist_items[index]
    else:
        print("playlist item is empty. choiced no video.")
        return None


def _create_youtube() -> Resource:
    MISSING_CLIENT_SECRETS_MESSAGE = "missing client secrets."
    YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    flow = flow_from_clientsecrets(
        _create_secret(), message=MISSING_CLIENT_SECRETS_MESSAGE, scope=YOUTUBE_READONLY_SCOPE
    )
    storage = Storage(_create_oauth())
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)

    youtube = build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http())
    )
    return youtube


def _create_secret() -> str:
    secret_path = "/tmp/sc_test.txt"
    with open(secret_path, "w") as st:
        load_dotenv(verbose=True)
        secret = os.environ.get("youtube_client_secret", "dummy")
        st.write(secret)
        st.close()
    return secret_path


def _create_oauth() -> str:
    oauth_path = "/tmp/oa_test.txt"
    with open(oauth_path, "w") as oa:
        load_dotenv(verbose=True)
        contents = os.environ.get("youtube_oauth_json", "dummy")
        oa.write(contents)
        oa.close()
    return oauth_path
