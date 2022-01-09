from typing import Dict, List
import requests
import json
from datetime import datetime

RESULTS_PATH = "data/results.json"

url = "https://www.thuistreffervechtdal.nl/portal/object/frontend/getallobjects/format/json"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.thuistreffervechtdal.nl/aanbod/te-huur",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Content-Length": "0",
    "Origin": "https://www.thuistreffervechtdal.nl",
    "Connection": "keep-alive",
    # "Cookie": "__Host-PHPSESSID=e0869ad39f9fa841d848df83b846a8c8; __Host-PHPSESSID=4915e54bc48417ca0f255635f95e552d",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
}


def scrape_listings():
    response = requests.request("POST", url, headers=headers)

    _res = json.loads(response.text)

    if _res and "result" in _res:

        with open(RESULTS_PATH, "r") as f:
            current_listings = json.loads(f.read())
            new_listings = _res["result"]
            new_listings = add_fields(new_listings)
            combined_listings = new_listings + current_listings
            deduplicated_listings = remove_duplicates(combined_listings)

            with open(RESULTS_PATH, "w") as f:
                f.write(json.dumps(deduplicated_listings, indent=4))


def convert_datetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def remove_duplicates(listings: List[Dict] = []) -> List[Dict]:
    filtered_listings: Dict[str, Dict] = {}

    url_keys: Dict[str, str] = {}
    for listing in listings:
        if "urlKey" not in listing:
            continue

        if listing["urlKey"] not in url_keys.items():
            filtered_listings[listing["urlKey"]] = listing

            if "publicationDate" in listing:
                url_keys[listing["urlKey"]] = listing["publicationDate"]
                continue
            else:
                print("No publication date for listing: {}".format(listing))
                continue

        elif listing["urlKey"] in url_keys:
            previous_date_str = url_keys[listing["urlKey"]]
            previous_date = convert_datetime(previous_date_str)
            current_date = convert_datetime(listing["publicationDate"])

            if current_date > previous_date:
                url_key = listing["urlKey"]
                url_keys[url_key] = listing["publicationDate"]
                filtered_listings[url_key] = listing
                print(
                    f"Newer listing found for {url_key}. Overwrititng".format(listing)
                )
                continue

    return [listing for listing in filtered_listings.values()]


def add_fields(listings: List[Dict] = []) -> List[Dict]:
    for listing in listings:
        listing[
            "url"
        ] = f"https://www.thuistreffervechtdal.nl/aanbod/te-huur/details/{listing['urlKey']}"
        listing["fields"] = listing.keys()
    return listings
