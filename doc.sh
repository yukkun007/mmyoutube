#!/bin/sh

if [ -e docs/conf.py ]; then
    sphinx-apidoc -f -o docs/ mmyoutube/  # 2回目以降
else
    sphinx-apidoc -F -o docs/ mmyoutube/  # 初回実行
fi
make -C docs/ html
