import logging
from dataclasses import dataclass
import dataclasses
import json
from typing import Dict, List, Optional

from utils.utils import convert_iso_date, convert_iso_datetime

RESULTS_PATH = "data/results.json"
BASE_URL = "https://www.dewoningzoeker.nl"

logger = logging.getLogger(__name__)


@dataclass
class Listing:
    url: str
    city: str
    corporation: str
    reactions: int
    rent: float
    rooms: Optional[int]
    year_built: str
    size: int
    availableFromDate: Optional[str]
    date_added: str
    picture_urls: List[str]
    picture_urls_str: str = ""
    id: Optional[int] = None
    address: str = ""
    postal_code: str = ""
    closing_date: str = ""
    dwelling_type: str = ""
    energy_label: str = ""

    def __post_init__(self):
        self.picture_urls_str = ", ".join(self.picture_urls)

    def as_dict(self):
        return dataclasses.asdict(self)


def load_listing(listing: Dict = {}) -> Listing:
    return Listing(
        availableFromDate=listing["availableFromDate"],
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
        id=listing.get("id"),
        address=listing.get("address", ""),
        postal_code=listing.get("postal_code", ""),
        closing_date=listing.get("closing_date", ""),
        dwelling_type=listing.get("dwelling_type", ""),
        energy_label=listing.get("energy_label", ""),
    )


def create_listing(listing: Dict = {}) -> Listing:
    available_from = listing.get("availableFromDate") or listing.get(
        "availableFromOriginalDate"
    )
    address = " ".join(
        str(part)
        for part in (
            listing.get("street"),
            listing.get("houseNumber"),
            listing.get("houseNumberAddition"),
        )
        if part
    )
    return Listing(
        availableFromDate=convert_iso_date(available_from),
        city=listing["city"]["name"],
        corporation=listing["corporation"]["name"],
        date_added=convert_iso_datetime(listing["publicationDate"]) or "",
        picture_urls=[
            f"{BASE_URL}{picture['uri']}" for picture in listing.get("pictures") or []
        ],
        reactions=listing["numberOfReactions"],
        rent=listing["totalRent"],
        rooms=(listing.get("sleepingRoom") or {}).get("amountOfRooms"),
        size=listing["areaDwelling"],
        url=f"{BASE_URL}/aanbod/te-huur/details/{listing['urlKey']}",
        year_built=str(listing.get("constructionYear") or ""),
        id=listing["id"],
        address=address,
        postal_code=listing.get("postalcode") or "",
        closing_date=convert_iso_datetime(listing.get("closingDate")) or "",
        dwelling_type=(listing.get("dwellingType") or {}).get("name") or "",
        energy_label=(listing.get("energyLabel") or {}).get("localizedNaam") or "",
    )


def remove_duplicatez(listings: List[Listing] = []) -> List[Listing]:
    listings_dict: Dict[str, Listing] = {}

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
        current_urls = {listing.url for listing in current_listings}
        new_count = len({l.url for l in listings if l.url not in current_urls})
        combined_listings = listings + current_listings
        deduplicated_listings = remove_duplicatez(combined_listings)
        logger.info(
            f"{new_count} new listings found, {len(deduplicated_listings)} in total."
        )
        write_listings(deduplicated_listings)
