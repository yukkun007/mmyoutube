# import sys
from .youtube import random_get_video


def main():
    random_get_video()
    # if len(sys.argv) == 3:
    #     x, y = map(int, sys.argv[1:])
    #     print(add(x, y))
    # else:
    #     print("please specify 2 arguments", file=sys.stderr)
    #     sys.exit(1)


if __name__ == "__main__":
    main()
