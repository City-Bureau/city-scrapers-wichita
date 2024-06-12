from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import BOARD, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wicks_goddard_boe import WicksGoddardBoeSpider

test_response = file_response(
    join(dirname(__file__), "files", "wicks_goddard_boe.json"),
    url="https://go.boarddocs.com/ks/usd265/Board.nsf/Public",
)
test_response_detail = file_response(
    join(dirname(__file__), "files", "wicks_goddard_boe_detail.html"),
    url="https://go.boarddocs.com/ks/usd265/Board.nsf/Public",
)
spider = WicksGoddardBoeSpider()

freezer = freeze_time("2024-02-22")
freezer.start()

# parse_detail expects a response object with a meta attribute
# containing the start date and meeting id
test_response_detail.meta["start_date"] = datetime(2024, 2, 19, 0, 0)
test_response_detail.meta["meeting_id"] = "CT23380490B4"
test_response_detail.meta["links"] = []
parsed_items = [item for item in spider.parse(test_response)]
parsed_item = next(spider._parse_detail(test_response_detail))
freezer.stop()


def test_count():
    assert len(parsed_items) == 4  # noqa


def test_title():
    assert parsed_item["title"] == "Regular Meeting"  # noqa


def test_description():
    assert (
        parsed_item["description"]
        == "Goddard USD No. 265 Board of Education Meeting Administration Center Board of Education Room 201 S. Main, Goddard, KS 7:00 pm"  # noqa
    )


def test_start():
    assert parsed_item["start"] == test_response_detail.meta["start_date"]


def test_end():
    assert parsed_item["end"] is None  # Assuming end time is not provided


def test_time_notes():
    assert parsed_item["time_notes"] == ""  # Assuming empty time notes


def test_id():
    assert (
        parsed_item["id"] == "wicks_goddard_boe/202402190000/x/regular_meeting"
    )  # noqa


def test_status():
    assert parsed_item["status"] == PASSED


def test_location():
    assert parsed_item["location"] == {
        "name": "Goddard USD 265 Administration Center",
        "address": "201 S Main St, Goddard, KS 67052",
    }


def test_source():
    assert (
        parsed_item["source"] == "https://go.boarddocs.com/ks/usd265/Board.nsf/Public"
    )  # noqa


def test_links():
    assert parsed_item["links"] == []  # Assuming no links provided


def test_classification():
    assert parsed_item["classification"] == BOARD


def test_all_day():
    assert parsed_item["all_day"] is False
