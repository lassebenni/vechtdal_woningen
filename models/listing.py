from dataclasses import dataclass
import dataclasses
from typing import Dict, List

from utils.utils import convert_datetime


@dataclass
class Listing:
    url: str
    city: str
    corporation: str
    reactions: int
    rent: float
    rooms: int
    year_built: int
    size: int
    availableFromDate: str
    date_added: str
    pictures: List[str]

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
        pictures=listing["pictures"],
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
        pictures=[
            f"https://www.thuistreffervechtdal.nl{picture['uri']}"
            for picture in listing["pictures"]
        ],
        reactions=listing["numberOfReactions"],
        rent=listing["totalRent"],
        rooms=listing["sleepingRoom"]["amountOfRooms"],
        size=listing["areaDwelling"],
        url=f"https://www.thuistreffervechtdal.nl/aanbod/te-huur/details/{listing['urlKey']}",
        year_built=listing["constructionYear"],
    )
