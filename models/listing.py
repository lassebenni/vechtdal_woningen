import logging
from dataclasses import dataclass
import dataclasses
import json
from typing import Dict, List

from utils.utils import convert_datetime

RESULTS_PATH = "data/results.json"

logger = logging.getLogger(__name__)


@dataclass
class Listing:
    url: str
    city: str
    corporation: str
    reactions: int
    rent: float
    rooms: int
    year_built: str
    size: int
    availableFromDate: str
    date_added: str
    picture_urls: List[str]
    picture_urls_str: str = ""

    def __post_init__(self):
        self.picture_urls_str = ", ".join(self.picture_urls)

    def as_dict(self):
        return dataclasses.asdict(self)


def load_listing(listing: Dict = {}) -> Listing:
    return Listing(
        availableFromDate=convert_datetime(
            listing["availableFromDate"], format="%Y-%m-%d %H:%M:%S"
        ),
        city=listing["city"],
        corporation=listing["corporation"],
        date_added=listing["date_added"],
        picture_urls=listing["picture_urls"],
        reactions=listing["reactions"],
        rent=listing["rent"],
        rooms=listing["rooms"],
        size=listing["size"],
        url=listing["url"],
        year_built=listing["year_built"],
    )


def create_listing(listing: Dict = {}) -> Listing:
    return Listing(
        availableFromDate=convert_datetime(listing["availableFromDate"], "%Y-%m-%d"),
        city=listing["city"]["name"],
        corporation=listing["corporation"]["name"],
        date_added=listing["publicationDate"],
        picture_urls=[
            f"https://www.thuistreffervechtdal.nl{picture['uri']}"
            for picture in listing["pictures"]
        ],
        reactions=listing["numberOfReactions"],
        rent=listing["totalRent"],
        rooms=listing["sleepingRoom"]["amountOfRooms"],
        size=listing["areaDwelling"],
        url=f"https://www.thuistreffervechtdal.nl/aanbod/te-huur/details/{listing['urlKey']}",
        year_built=str(listing["constructionYear"]),
    )


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


def store_listings(listings: List[Listing] = []):
    with open(RESULTS_PATH, "r") as f:
        results_file = json.loads(f.read())
        current_listings = [load_listing(listing) for listing in results_file]
        combined_listings = listings + current_listings
        deduplicated_listings = remove_duplicatez(combined_listings)
        logger.info(f"{len(deduplicated_listings)} new listings found.")
        write_listings(deduplicated_listings)
