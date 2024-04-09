from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wicks_sedgwick_jcab import WicksSedgwickJcabSpider

test_response = file_response(
    join(dirname(__file__), "files", "wicks_sedgwick_jcab.html"),
    url="https://www.sedgwickcounty.org/corrections/corrections-advisory-boards/",
)
spider = WicksSedgwickJcabSpider()

freezer = freeze_time("2024-04-03")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

"""
Arbitrary number of items. 36 is the returned number
of items from the spider.
"""


def test_count():
    assert len(parsed_items) == 36


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Juvenile Corrections Advisory Board Monthly Meeting"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 1, 12, 11, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 1, 12, 13, 00)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "wicks_sedgwick_jcab/202401121130/x/juvenile_corrections_advisory_board_monthly_meeting"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "271 W. 3rd St. N., 3rd Floor, Wichita, KS",
        "name": "Ronald Reagan Building",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.sedgwickcounty.org/corrections/corrections-advisory-boards/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.sedgwickcounty.org/media/65784/tj-agenda-1-12-24.pdf",
            "title": "Agenda",
        },
        {
            "href": "https://www.sedgwickcounty.org/media/66261/1-12-24-team-justice-minutes.docx",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://us02web.zoom.us/j/84774230090?pwd=UkpNUFFaUElta01pTTdPbHM3T2VGdz09",  # noqa
            "title": "Join Zoom Meeting",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
