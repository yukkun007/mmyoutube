import random
import re
import logging
from typing import List, Union, Dict, Callable, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import Resource
from googleapiclient.http import HttpRequest
from mmyoutube.video import Video
from mmyoutube.youtube import create_youtube
from mmyoutube.youtube_new import Youtube


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def random_get_video(dotenv_path: str = None) -> Union[None, Video]:
    return _get_video(_filter_none, dotenv_path)


def _filter_none(items: List[Dict]) -> List[Dict]:
    return items


def get_video_match_today(dotenv_path: str = None) -> Union[None, Video]:
    return _get_video(_filter_match_today, dotenv_path)


def _filter_match_today(items: List[Dict]) -> List[Dict]:
    return list(filter(lambda item: _is_match_today(item["snippet"]["title"]), items))


def _is_match_today(content: str) -> bool:
    pattern = re.compile(r"^2\d{3}" + datetime.now().strftime("/%m/%d"))
    if re.search(pattern, content):
        print("matched video title on today! content=" + content)
        return True
    else:
        return False


def get_videos_within_x_day(x: float = 7, dotenv_path: str = None) -> List[Video]:
    return _get_videos(_filter_within_x_day, {"within_x_day": x}, dotenv_path)


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


def _get_video(
    filter_method: Callable[[List[Dict]], List[Dict]], dotenv_path: str = None
) -> Union[None, Video]:
    youtube = create_youtube(dotenv_path)

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
    choice = _choice_playlist_item(tmp_choiced_items)
    if choice is not None:
        return Video(choice)
    else:
        return None


def _get_videos(
    filter_method: Callable[[List[Dict], float], List[Dict]], param: Dict, dotenv_path: str = None
) -> List[Video]:
    youtube = create_youtube(dotenv_path)

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


def _choice_playlist_item(playlist_items: List[Dict]) -> Optional[Dict]:
    items_number = len(playlist_items)
    if items_number > 0:
        index = random.randint(0, items_number - 1)
        print("video choice done. choiced_index={} from {}videos.".format(index, items_number))
        return playlist_items[index]
    else:
        print("playlist item is empty. choiced no video.")
        return None


def get_play_list(dotenv_path: str = None) -> None:
    youtube = Youtube(dotenv_path=dotenv_path)

    params = {"part": "snippet", "mine": True}
    # リクエスト送信
    response = youtube.get(Youtube.api_url.get("playlists"), params=params)
    # logger.debug(response.text)
    assert response.status_code == 200, "Response is not 200"
    res_json = response.json()
    logger.debug(res_json)
