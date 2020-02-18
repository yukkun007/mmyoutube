import logging
from mmyoutube.youtube_new import Youtube

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def add_to_play_list(play_list_id: str, vidoe_id: str) -> None:
    youtube = Youtube()

    # パラメータ
    params = {"part": "snippet"}
    # リクエストボディ
    request_body = {
        "snippet": {
            "playlistId": play_list_id,
            "resourceId": {"kind": "youtube#video", "videoId": vidoe_id},
        }
    }
    # リクエスト送信
    api_url = Youtube.api_url.get("playlistItems")
    response = youtube.post(api_url, params=params, json=request_body)
    # logger.debug(response.text)
    assert response.status_code == 200, "Response is not 200"

    res_json = response.json()
    # logger.debug(res_json)
    playlist_item_id = res_json.get("id")
    snippet = res_json.get("snippet")
    resource_id = snippet.get("resourceId")
    logger.debug(
        "add video to playlist. {} -> {}".format(
            resource_id.get("videoId"), snippet.get("playlistId")
        )
    )

    # 追加したplaylistItemのIDを返します
    # playlistから削除するには、playlistItemsに対してこのIDを指定してDELETEを呼びます
    return playlist_item_id


def delete_from_play_list(play_list_item_id: str) -> None:
    youtube = Youtube()

    # パラメータ
    params = {"id": play_list_item_id}
    # リクエスト送信
    api_url = Youtube.api_url.get("playlistItems")
    response = youtube.delete(api_url, params=params)
    # logger.debug(response.text)
    assert response.status_code == 204, "Response is not 204"
