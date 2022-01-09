import logging
from typing import Dict, List
import requests
import json

from models.listing import Listing, create_listing, store_listings

logger = logging.getLogger(__name__)


URL = "https://www.thuistreffervechtdal.nl/portal/object/frontend/getallobjects/format/json"

HEADERS = {
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
    response = requests.request("POST", URL, headers=HEADERS)

    _res = json.loads(response.text)

    if _res and "result" in _res:

        fetched_listings: List[Listing] = []
        for listing in _res["result"]:
            detailed_listing = fetch_detailed_listing(listing["id"])
            fetched_listings.append(create_listing(detailed_listing))

        if fetched_listings:
            store_listings(fetched_listings)
        else:
            logger.info("No listings found.")


def fetch_detailed_listing(listing_id: str):
    url = "https://www.thuistreffervechtdal.nl/portal/object/frontend/getobject/format/json"
    response = requests.request("POST", url, headers=HEADERS, data=f"id={listing_id}")

    _res = json.loads(response.text)

    if _res and "result" in _res:
        listing = _res["result"]
        return listing
    else:
        print(f"No listing found for id: {listing_id}")
        return None
