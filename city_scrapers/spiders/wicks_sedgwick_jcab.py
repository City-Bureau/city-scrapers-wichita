import re
from datetime import datetime, time
from urllib.parse import urljoin

from city_scrapers_core.constants import BOARD, CANCELLED, PASSED, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class WicksSedgwickJcabSpider(CityScrapersSpider):
    name = "wicks_sedgwick_jcab"
    agency = "Sedgwick County - Juvenile Corrections Advisory Board"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.sedgwickcounty.org/corrections/corrections-advisory-boards/"
    ]

    start = time(11, 30)
    end = time(13, 0)
    location = {
        "address": "271 W. 3rd St. N., 3rd Floor, Wichita, KS",
        "name": "Ronald Reagan Building",
    }

    """
    The Zoom link is the same for all the meetings, so it is added as a class attribute.
    """
    zoom_link = {
        "href": "https://us02web.zoom.us/j/84774230090?pwd=UkpNUFFaUElta01pTTdPbHM3T2VGdz09",  # noqa
        "title": "Join Zoom Meeting",
    }

    def parse(self, response):
        meetings = response.css(
            "article.inSection div ul li:contains('Agenda'):contains('Minutes')"
        )

        for item in meetings:
            meeting = Meeting(
                title="Juvenile Corrections Advisory Board Monthly Meeting",
                description="",
                classification=BOARD,
                start=self._parse_date(item, self.start),
                end=self._parse_date(item, self.end),
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(response, item),
                source=response.url,
            )

            meeting["status"] = self._get_status(item)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_links(self, response, item):
        links = item.css("a")
        parsed_links = []
        for link in links:
            link_text = link.css("::text").get()
            if "agenda" in link_text.lower():
                agenda_link = link.css("::attr(href)").get()
                parsed_links.append(
                    {"href": urljoin(response.url, agenda_link), "title": "Agenda"}
                )
            elif "minutes" in link_text.lower():
                minutes_link = link.css("::attr(href)").get()
                parsed_links.append(
                    {"href": urljoin(response.url, minutes_link), "title": "Minutes"}
                )
        parsed_links.append(self.zoom_link)

        return parsed_links

    def _get_status(self, item):
        """
        This method is overridden since the meetings'
        title is always the same, and the description
        field is empty. The meeting details coming from
        the 'item' are extracted from an <li> tag as part
        of a single line which combines meeting date,
        agenda & minutes links, and a status (only if a meeting is 'CANCELLED').
        """
        cancelled = item.get().lower()
        start = self._parse_date(item, self.start)

        if "cancel" in cancelled:
            return CANCELLED
        if start < datetime.now():
            return PASSED
        return TENTATIVE

    def _parse_date(self, item, hour):
        details_split = item.css("li::text").get().split("-")
        date_obj = re.search(r"\b(\w+ \d{1,2}, \d{4})\b", details_split[0]).group(0)
        date = datetime.strptime(date_obj, "%B %d, %Y")

        return datetime.combine(date, hour)
