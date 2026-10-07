import json
from pathlib import Path

from models.listing import create_listing, load_listing

FIXTURE = Path(__file__).parent / "fixtures" / "listing.json"


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_create_listing():
    listing = create_listing(load_fixture())

    assert (
        listing.url
        == "https://www.dewoningzoeker.nl/aanbod/te-huur/details/41599-akelei-16-kampen"
    )
    assert listing.city == "Kampen"
    assert listing.rent == 634.44
    assert listing.id == 41599
    assert listing.address.startswith("Akelei 16")
    assert listing.picture_urls[0].startswith(
        "https://www.dewoningzoeker.nl/portal/uploads/"
    )
    # publicationDate 10:00 UTC is 12:00 in Amsterdam (summer time)
    assert listing.date_added == "2026-10-07 12:00:00"
    # availableFromDate is null, falls back to availableFromOriginalDate
    assert listing.availableFromDate == "2026-11-20 00:00:00"


def test_round_trip_new_listing():
    listing = create_listing(load_fixture())
    stored = json.loads(json.dumps(listing.as_dict(), default=str))

    assert load_listing(stored).url == listing.url


def test_load_old_listing():
    old = {
        "availableFromDate": "2023-07-05 00:00:00",
        "city": "De Krim",
        "corporation": "Vechtdal Wonen",
        "date_added": "2023-06-12 09:03:00",
        "picture_urls": [],
        "picture_urls_str": "",
        "reactions": 86,
        "rent": 688.05,
        "rooms": "4",
        "size": 70,
        "url": "https://www.thuistreffervechtdal.nl/aanbod/te-huur/details/3514-x",
        "year_built": "1975",
    }

    listing = load_listing(old)

    assert listing.city == "De Krim"
    assert listing.address == ""
    assert listing.id is None
