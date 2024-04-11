from urllib.parse import urljoin

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse
import pdb


class WicksBoccSpider(CityScrapersSpider):
    name = "wicks_bocc"
    agency = "Board of Sedgwick County Commissioners"
    timezone = "America/Chicago"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }
    # original https://www.sedgwickcounty.org/commissioners/commission-meetings/
    # original page embeds iframe with the following URL
    # we scrape the embedded URL instead
    start_urls = ["https://sedgwick.granicus.com/ViewPublisher.php?view_id=34"]
    time_notes = "Refer to agenda for start time or contact agency for details."
    location = {
        "name": "Ruffin Auditorium",
        "address": "100 N. Broadway, Lower Level, Wichita, KS 67202",
    }

    def parse(self, response):
        """Parse meeting items from agency website iframe."""

        # get upcoming events
        for item in response.css("table")[0].css("tbody tr"):
            meeting = Meeting(
                title=item.css("td")[0].css("::text").get(),
                description="",
                classification=COMMISSION,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes=self.time_notes,
                location=self.location,
                links=self._parse_links(response, item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        # get archived events in current year. ignore all other years
        for item in response.css(".TabbedPanelsContent")[0].css("table tbody tr"):
            # skip if row does not have enough data cells to avoid IndexErrors
            if len(item.css("td")) < 2:
                continue

            meeting = Meeting(
                title=item.css("td")[0].css("::text").get(),
                description="",
                classification=COMMISSION,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self.location,
                links=self._parse_links(response, item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """
        Parse start date as a naive datetime object.
        Fetch from correct table cell and clean up.
        """

        date_cell = item.css("td")[1]
        raw_date = date_cell.css("::text").get()
        clean_date = raw_date.strip().replace("\xa0", " ")
        parsed_date = parse(clean_date)

        return parsed_date

    def _parse_links(self, response, item):
        """Parse or generate links like Agenda or Video links."""
        output = []

        # find all links in table row
        links = item.css("a")

        for link in links:
            title = link.css("::text").get()
            # find URL based on link title
            if title and "Video" in title:
                link_url = link.css("::attr(onclick)").get().split("'")[1]
                full_url = urljoin(response.url, link_url)
                output.append({"title": "Video", "href": full_url})
            else:
                link_url = link.css("::attr(href)").get()
                full_url = urljoin(response.url, link_url)
                output.append({"title": title, "href": full_url})

        return output
