import logging
from typing import Dict, List, Union

import requests

from models.listing import Listing, create_listing, store_listings

logger = logging.getLogger(__name__)


URL = "https://dewoningzoeker-aanbodapi.zig365.nl/api/v1/actueel-aanbod"
PAGE_SIZE = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:156.0) Gecko/20100101 Firefox/156.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.dewoningzoeker.nl",
    "Referer": "https://www.dewoningzoeker.nl/",
}

# Same filters the website sends for anonymous visitors: all rental homes.
BODY = {
    "hidden-filters": {
        "$and": [
            {"dwellingType.categorie": {"$eq": "woning"}},
            {"rentBuy": {"$eq": "Huur"}},
            {"isExtraAanbod": {"$eq": ""}},
            {"isWoningruil": {"$eq": ""}},
        ]
    }
}


def fetch_page(page: int) -> Dict:
    params: Dict[str, Union[str, int]] = {
        "limit": PAGE_SIZE,
        "locale": "nl_NL",
        "page": page,
        "sort": "-publicationDate",
    }
    response = requests.post(URL, headers=HEADERS, params=params, json=BODY, timeout=30)
    response.raise_for_status()
    return response.json()


def scrape_listings():
    fetched_listings: List[Listing] = []

    page, page_count = 0, 1
    while page < page_count:
        _res = fetch_page(page)
        page_count = _res["_metadata"]["page_count"]

        for listing in _res["data"]:
            try:
                fetched_listings.append(create_listing(listing))
            except Exception:
                logger.exception(f"Error while parsing listing: {listing.get('id')}")
                continue

        page += 1

    if fetched_listings:
        store_listings(fetched_listings)
    else:
        logger.info("No listings found.")
