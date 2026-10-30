#!/usr/bin/env bash
set -e
source venv/bin/activate

python3 scrape_url.py > url_test.txt
head -n 150 url_test.txt | python3 scrape_data.py > data.tsv