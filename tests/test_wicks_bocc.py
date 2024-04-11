from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.wicks_bocc import WicksBoccSpider

test_response = file_response(
    join(dirname(__file__), "files", "wicks_bocc.html"),
    url="https://sedgwick.granicus.com/ViewPublisher.php?view_id=34",
)
spider = WicksBoccSpider()

freezer = freeze_time("2024-04-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 51


def test_title():
    assert parsed_items[0]["title"] == "Governing Body of Fire District 1"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 4, 10, 0, 0)
    assert parsed_items[3]["start"] == datetime(2024, 4, 4, 0, 0)


def test_end():
    assert parsed_items[0]["end"] == None
    assert parsed_items[3]["end"] == None


def test_time_notes():
    # only upcoming events get time notes
    assert parsed_items[0]["time_notes"] == "Refer to agenda for start time or contact agency for details."
    # archived events do not get time notes
    assert parsed_items[3]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "wicks_bocc/202404100000/x/governing_body_of_fire_district_1"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Ruffin Auditorium",
        "address": "100 N. Broadway, Lower Level, Wichita, KS 67202",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://sedgwick.granicus.com/ViewPublisher.php?view_id=34"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sedgwick.granicus.com/AgendaViewer.php?view_id=34&event_id=1912",  # noqa
        }
    ]
    assert parsed_items[3]["links"] == [
        {
            "title": "Video",
            "href": "https://sedgwick.granicus.com/MediaPlayer.php?view_id=34&clip_id=5350",  # noqa
        }
    ]
    assert parsed_items[30]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sedgwick.granicus.com/AgendaViewer.php?view_id=34&clip_id=5322",  # noqa
        },
        {
            'title': 'Minutes',
            'href': 'https://sedgwick.granicus.com/MinutesViewer.php?view_id=34&clip_id=5322&doc_id=dac37c29-e850-11ee-98bb-0050569183fa',  # noqa
        },
        {
            'title': 'Video',
            'href': 'https://sedgwick.granicus.com/MediaPlayer.php?view_id=34&clip_id=5322',  # noqa
        },

    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
