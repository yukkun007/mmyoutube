import os
import argparse
from mmyoutube import random_get_video, upload, UploadOption

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def main():
    parser = argparse.ArgumentParser(
        description="""
    YouTube動画を操作します。
    """
    )

    parser.add_argument("--file", help="Video file to upload")
    parser.add_argument("--title", help="Video title", default="Test Title")
    parser.add_argument("--description", help="Video description", default="Test Description")
    parser.add_argument(
        "--category",
        default="22",
        help="Numeric video category. "
        + "See https://developers.google.com/youtube/v3/docs/videoCategories/list",
    )
    parser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    parser.add_argument(
        "--privacyStatus",
        choices=VALID_PRIVACY_STATUSES,
        default=VALID_PRIVACY_STATUSES[0],
        help="Video privacy status",
    )
    parser.add_argument("--mode", choices=("upload", "get"), help="Mode of operation")

    args = parser.parse_args()

    if args.mode == "upload":
        if args.file is None or not os.path.exists(args.file):
            exit("Please specify a valid file using the --file= parameter.")
        upload(UploadOption(args))
    elif args.mode == "get":
        random_get_video()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
