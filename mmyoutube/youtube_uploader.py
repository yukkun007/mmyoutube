import os
import time
import random
import http.client
import httplib2
import logging
from typing import Optional
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from mmyoutube.upload_option import UploadOption
from mmyoutube.youtube import create_youtube


# logger
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


def upload(options: UploadOption, dotenv_path: str = None) -> Optional[str]:
    if not os.path.exists(options.file):
        logger.error("not specified valid file to upload. options.file={}".format(options.file))
        return None

    youtube = create_youtube(dotenv_path=dotenv_path)
    try:
        return _initialize_upload(youtube, options)
    except HttpError as e:
        logger.error("An HTTP error {} occurred:\n{}".format(e.resp.status, e.content))

    return None


def _initialize_upload(youtube: Resource, options: UploadOption) -> Optional[str]:
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category,
        ),
        status=dict(privacyStatus=options.privacyStatus),
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True),
    )

    return _resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def _resumable_upload(insert_request) -> Optional[str]:
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.info("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" in response:
                    id = response["id"]
                    logger.info("Video id {} was successfully uploaded.".format(id))
                    return id
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            logger.error(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            logger.info("Sleeping {} seconds and then retrying...".format(sleep_seconds))
            time.sleep(sleep_seconds)

    return None
