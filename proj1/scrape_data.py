############################################################
### Authors: Matej Melchiory, David Navrátil
### Date: 29.9.2026
### Description: Scraping product URLs from simpletire.com
############################################################

import sys
import time
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

    """ Save HTML for inspection
        with open("product.html", "w", encoding="utf-8") as file:
            file.write(resp.text)
    """

    # Parse HTML
    soup = BeautifulSoup(resp.text, "lxml")

    # Find product name
    # If product sites are consistent - name = soup.find("h1").get_text(strip=True)
    name_tag = soup.find("h1")

    if name_tag:
        name = name_tag.get_text(strip=True)
    else:
        name = ""

    # Find the tire size from the URL
    tire_size = url.split("tireSize=")[1].split("&")[0]

    # Find the matching tire size block and its price
    price = ""

    for li in soup.find_all("li", attrs={"data-component": "TireSize"}):
        link = li.find("a", attrs={"data-component": "BaseLinkInner"})

        if link and tire_size in link.get("href", ""):
            price_tag = li.find(
                "p",
                attrs={"data-component": "TireSizePrice"}
            )

            if price_tag:
                price = price_tag.get_text(strip=True)

            break

    row = [
        url,
        name,
        price
    ]

    return row

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