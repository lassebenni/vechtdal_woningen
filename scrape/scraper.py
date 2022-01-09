import logging
from typing import Dict, List
import requests
import json

from models.listing import Listing, create_listing, load_listing

logger = logging.getLogger(__name__)

RESULTS_PATH = "data/results.json"

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
        fetched_listings = []
        for listing in _res["result"]:
            detailed_listing = fetch_detailed_listing(listing["id"])
            fetched_listings.append(create_listing(detailed_listing))

        if fetched_listings:
            with open(RESULTS_PATH, "r") as f:
                results_file = json.loads(f.read())
                current_listings = [load_listing(listing) for listing in results_file]
                combined_listings = fetched_listings + current_listings
                deduplicated_listings = remove_duplicatez(combined_listings)
                logger.info(f"{len(deduplicated_listings)} new listings found.")
                write_listings(deduplicated_listings)
        else:
            logger.info("No listings found.")


def remove_duplicatez(listings: List[Listing] = []) -> List[Listing]:
    listings_dict = {}

    for listing in listings:
        if listing.url not in listings_dict:
            listings_dict[listing.url] = listing
        else:
            if listing.date_added > listings_dict[listing.url].date_added:
                listings_dict[listing.url] = listing

    return [listing for listing in listings_dict.values()]


def write_listings(listings: List[Listing] = []):
    listing_dicts: List[Dict] = [listing.as_dict() for listing in listings]
    with open(RESULTS_PATH, "w") as f:
        f.write(json.dumps(listing_dicts, indent=4, default=str, sort_keys=True))


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
