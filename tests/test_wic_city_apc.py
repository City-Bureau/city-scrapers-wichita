from datetime import datetime
from os.path import dirname, join

import pytest  # noqa: F401
from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wic_city_apc import WicCityApcSpider

test_response = file_response(
    join(dirname(__file__), "files", "wic_city_apc.html"),
    url="https://www.wichita.gov/calendar.aspx?Keywords=&startDate=01/01/2024&enddate=04/30/2024&CID=68&showPastEvents=true",  # noqa: E501
)
test_detail_response = file_response(
    join(dirname(__file__), "files", "wic_city_apc_detail.html"),
    url="https://www.wichita.gov/Calendar.aspx?EID=1592&month=2&year=2024&day=13&calType=0",  # noqa: E501
)
spider = WicCityApcSpider()

freezer = freeze_time("2024-02-13")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_item = next(spider._parse_detail(test_detail_response))


freezer.stop()


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_item["title"] == "Advance Plans Committee Meeting"


def test_description():
    expected_start = "Meeting Options to Participate The Advance Plans Committee meetings are open to the publi"  # noqa: E501
    assert parsed_item["description"][:89] == expected_start


def test_classification():
    assert parsed_item["classification"] == COMMITTEE


def test_start():
    assert parsed_item["start"] == datetime(2024, 6, 13, 10, 0)


def test_end():
    assert parsed_item["end"] == datetime(2024, 6, 13, 11, 30)


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert (
        parsed_item["id"]
        == "wic_city_apc/202406131000/x/advance_plans_committee_meeting"
    )


def test_status():
    assert parsed_item["status"] == TENTATIVE


def test_location():
    assert parsed_item["location"] == {
        "name": "2nd Floor Large Conference Room",
        "address": "271 W. 3rd St., Wichita, KS 67202",
    }


def test_source():
    assert (
        parsed_item["source"]
        == "https://www.wichita.gov/Calendar.aspx?EID=1592&month=2&year=2024&day=13&calType=0"  # noqa: E501
    )  # noqa: E501


def test_links():
    assert parsed_item["links"] == WicCityApcSpider.links


def test_all_day():
    assert parsed_item["all_day"] is False
