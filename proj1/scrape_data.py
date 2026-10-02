############################################################
### Authors: David Navrátil, Matej Melchiory
### Date: 29.9.2026
### Description: Scraping product data from simpletire.com
############################################################

#!/usr/bin/env python3

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
    # Download the product page
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

    # Parse the downloaded HTML
    soup = BeautifulSoup(resp.text, "lxml")

    # Find product name
    # If product sites are consistent - name = soup.find("h1").get_text(strip=True)
    name_tag = soup.find("h1")

    if name_tag:
        name = name_tag.get_text(strip=True)
    else:
        name = ""

    # Get the tire size from the product URL
    tire_size = url.split("tireSize=")[1].split("&")[0]

    # Initialize product values
    price = ""
    width = ""
    ratio = ""
    inflation_pressure = ""
    tread_depth = ""
    sidewall = ""

    # Find the tire size block matching the URL
    for li in soup.find_all("li", attrs={"data-component": "TireSize"}):
        link = li.find("a", attrs={"data-component": "BaseLinkInner"})

        if link and tire_size in link.get("href", ""):
            # Find the price for this tire size
            price_tag = li.find("p", attrs={"data-component": "TireSizePrice"})

            if price_tag:
                price = price_tag.get_text(strip=True)

            # Find technical specifications for this tire size
            specs = li.find("table", {"data-component": "TireSizeSpecs"})

            if specs:
                for spec in specs.find_all("tr", {"data-component": "TireSizeSpec"}):
                    label = spec.find("th").get_text(strip=True)
                    value = spec.find("td").get_text(strip=True)

                    if label == "Width":
                        width = value
                    elif label == "Ratio":
                        ratio = value
                    elif label == "Inflation Pressure":
                        inflation_pressure = value
                    elif label == "Tread Depth":
                        tread_depth = value
                    elif label == "Sidewall":
                        sidewall = value

            break

    specs = li.find("table", {"data-component": "TireSizeSpecs"})

    # Create one TSV row
    row = [
        url,
        name,
        price,
        width,
        ratio,
        inflation_pressure,
        tread_depth,
        sidewall
    ]

    return row

def main():
    # Read product URLs from standard input
    for line in sys.stdin:
        url = line.strip()

        if not url:
            continue

        # Scrape data for the current product
        row = scrape_product(url)

        # Print the result as a TSV row
        if row:
            print("\t".join(row))

        # Wait before requesting the next product
        time.sleep(DELAY)

if __name__ == "__main__":
    main()