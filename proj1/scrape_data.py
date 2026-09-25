import sys
import time
import re
import requests
from bs4 import BeautifulSoup

# Delay between requests to avoid overwhelming the server
DELAY = 1
# Our own headers
HEADERS = {
    "User-Agent":   "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
}

def scrape_product(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"Error {resp.status_code} for {url}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Request failed for {url}: {e}", file=sys.stderr)
        return None

    # TODO

def main():
    for line in sys.stdin:
        url = line.strip()
        if not url:
            continue

        row = scrape_product(url)
        if row:
            print("\t".join(row))
        
        time.sleep(DELAY)

if __name__ == "__main__":
    main()