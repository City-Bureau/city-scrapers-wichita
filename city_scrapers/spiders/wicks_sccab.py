import re
from urllib.parse import urljoin

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class WicksSccabSpider(CityScrapersSpider):
    name = "wicks_sccab"
    agency = "Sedgwick County: Corrections Advisory Boards"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.sedgwickcounty.org/corrections/corrections-advisory-boards/"
    ]

    def parse(self, response):
        """Parse meeting items from agency website."""
        start_time = "8 a.m."
        end_time = "9 a.m."
        location = {
            "name": "Adult Field Services",
            "address": "905 N. Main, Wichita, Kansas",
        }
        for item in response.css("h4:nth-of-type(2) + *").css("li"):
            date = re.search(r"\D+ \d+, \d+", item.css("::text").get()).group()
            meeting = Meeting(
                title="Community Corrections Advisory Board Monthly Meeting",
                description=self._parse_description(item),
                classification=BOARD,
                start=self._parse_start(date, start_time),
                end=self._parse_end(date, end_time),
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(response, item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_description(self, item):
        """
        Parse description.
        Used to indicate if meeting has been cancelled.
        Helps _get_status function set status correctly.
        """
        text = item.get().lower()
        return "CANCELLED" if "cancel" in text else ""

    def _parse_start(self, date, start_time):
        """
        Parse start datetime as a naive datetime object.
        Combine date from page and hardcoded time.
        """
        parsed_datetime = parse(f"{date} {start_time}")
        return parsed_datetime

    def _parse_end(self, date, end_time):
        """
        Parse end datetime as a naive datetime object.
        Combine date from page and hardcoded time.
        """
        parsed_datetime = parse(f"{date} {end_time}")
        return parsed_datetime

    def _parse_links(self, response, item):
        """
        Parse links. Agenda for date is sometimes present.
        Minutes link for year is usually present.
        Add both if found.
        """
        output = []
        links = item.css("a")
        for link in links:
            title = link.css("::text").get()
            href = link.css("::attr(href)").get()
            url = urljoin(response.url, href)

            output.append({"title": title, "href": url})

        return output
