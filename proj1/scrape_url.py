############################################################
### Authors: Matej Melchiory, David Navrátil
### Date: 25.9.2026
### Description: Scraping product URLs from simpletire.com
############################################################

#!/usr/bin/env python3

import sys
import time
import random
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup

# Our chosen URL
URL = "https://simpletire.com/"
# Delay between requests to avoid overwhelming the server
DELAY = 1
# Maximum number of product URLs taken from one brand
MAX_PER_BRAND = 30
# Total number of product URLs we want
TOTAL = 150
# Our own headers
HEADERS = {
    "User-Agent":   "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
}

# Getting a response from the URL
response = requests.get(URL, headers=HEADERS, timeout=10)
html = response.text

# Finding all model links using regex
model_links = list(set(re.findall(r'https://simpletire\.com/brands/[a-z0-9-]+-tires/[a-z0-9-]+', html)))
# Different models are processed on every run
random.shuffle(model_links)

product_urls = []
seen = set()
# Number of product URLs already taken per brand
brand_counts = {}

# Going through all model links found and scraping the product URLs
for model_url in model_links:

    # Stopping at the required number of product URLs
    if len(product_urls) >= TOTAL:
        break

    # Brand is part of the URL: /brands/<brand>-tires/<model>
    brand = model_url.split("/brands/")[1].split("/")[0]

    # Skipping models of brands that already have enough products (no request needed)
    if brand_counts.get(brand, 0) >= MAX_PER_BRAND:
        continue

    # Getting a response from current model URL
    resp = requests.get(model_url, headers=HEADERS, timeout=10)

    # Delay to avoid overwhelming the server
    time.sleep(DELAY)

    # Checking if the response is successful
    if resp.status_code != 200:
        print(f"Skipping {model_url}: status {resp.status_code}", file=sys.stderr)
        continue

    # Parsing the HTML content of the model page
    model_soup = BeautifulSoup(resp.text, "lxml")
    # Every tire has a variety of sizes, so we can find the product URLs by looking at all possible sizes
    size_items = model_soup.find_all("li", attrs={"data-component": "TireSize"})

    # Collecting the product URLs of this model
    model_product_urls = []
    for li in size_items:
        link = li.find("a", attrs={"data-component": "BaseLinkInner"})
        if link is None:
            continue
        href = link.get("href")
        if href:
            full_url = urllib.parse.urljoin(model_url, href)
            if full_url not in seen:
                seen.add(full_url)
                model_product_urls.append(full_url)

    # Taking a random sample so the sizes are spread across all rims, not just the smallest ones
    free_slots = MAX_PER_BRAND - brand_counts.get(brand, 0)
    chosen = random.sample(model_product_urls, min(free_slots, len(model_product_urls)))
    product_urls.extend(chosen)
    brand_counts[brand] = brand_counts.get(brand, 0) + len(chosen)

    print(f"{model_url}: found {len(size_items)} sizes, took {len(chosen)} "
          f"(brand {brand}: {brand_counts[brand]}, total so far: {len(product_urls)})", file=sys.stderr)

# Printing all product URLs found, limited to TOTAL
for url in product_urls[:TOTAL]:
    print(url)