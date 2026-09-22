#!/bin/bash
set -e
source venv/bin/activate

python3 get_urls.py > url_test.txt
head -n 10 url_test.txt | python3 get_data.py