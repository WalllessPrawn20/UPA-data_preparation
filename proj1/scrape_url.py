############################################################
### Authors: Matej Melchiory, David Navrátil
### Date: 25.9.2026
### Description: Scraping product URLs from simpletire.com
############################################################


import sys
import time
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

# Our chosen URL
URL = "https://simpletire.com/"
# Delay between requests to avoid overwhelming the server
DELAY = 1
# Our own headers
HEADERS = {
    "User-Agent":   "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
}

# Getting a response from the URL
response = requests.get(URL, headers=HEADERS, timeout=10)
html = response.text

# Finding all model links using regex
model_links = set(re.findall(r'https://simpletire\.com/brands/[a-z0-9-]+-tires/[a-z0-9-]+', html))

product_urls = []

# Going through all model links found and scraping the product URLs
for model_url in model_links:

    # Stopping at 150 product URLs
    if len(product_urls) >= 150:
        break

    # Getting a response from current model URL
    resp = requests.get(model_url, headers=HEADERS, timeout=10)

    # Dellay to avoid overwhelming the server
    time.sleep(DELAY)

    # Checking if the response is successful
    if resp.status_code != 200:
        print(f"Skipping {model_url}: status {resp.status_code}", file=sys.stderr)
        continue

    # Parsing the HTML content of the model page
    model_soup = BeautifulSoup(resp.text, "lxml")
    # Every tire has a variety of sizes, so we can find the product URLs by looking at all possible sizes
    size_items = model_soup.find_all("li", attrs={"data-component": "TireSize"})

    # Going through all size items found and extracting the product URLs
    for li in size_items:
        link = li.find("a", attrs={"data-component": "BaseLinkInner"})
        if link is None:
            continue
        href = link.get("href")
        if href:
            full_url = urllib.parse.urljoin(model_url, href)
            product_urls.append(full_url)

    print(f"{model_url}: found {len(size_items)} sizes (total so far: {len(product_urls)})", file=sys.stderr)

# Printing all product URLs found, limited to 150
for url in product_urls[:150]:
    print(url)

