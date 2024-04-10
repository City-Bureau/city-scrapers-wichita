from urllib.parse import urljoin

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class WicksBoccSpider(CityScrapersSpider):
    name = "wicks_bocc"
    agency = "Board of Sedgwick County Commissioners"
    timezone = "America/Chicago"
    # original https://www.sedgwickcounty.org/commissioners/commission-meetings/
    # Original page embeds iframe with the following URL.
    # We scrape the embedded URL instead.
    start_urls = ["https://sedgwick.granicus.com/ViewPublisher.php?view_id=34"]
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
                end="",
                all_day=False,
                time_notes=self._parse_time_notes(item),
                location=self.location,
                links=self._parse_links(response, item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        # get archived events in current year
        for item in response.css(".TabbedPanelsContent")[0].css("table tbody tr"):
            # pdb.set_trace()
            # skip if row does not have enough data cells to avoid IndexErrors
            if len(item.css("td")) < 2:
                continue

            meeting = Meeting(
                title=item.css("td")[0].css("::text").get(),
                description="",
                classification=COMMISSION,
                start=self._parse_start(item),
                end="",
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

        # Attempt to get date
        try:
            date_cell = item.css("td")[1]
            raw_date = date_cell.css("::text").get()
            clean_date = raw_date.strip().replace("\xa0", " ")
            parsed_date = parse(clean_date)
        except IndexError:
            parsed_date = None

        return parsed_date

    def _parse_time_notes(self, item):
        """
        Parse any additional notes on the timing of the meeting.
        If Agenda link is given, meeting start time may be found in there.
        Eventually we could scrape the link
        but for now we can just tell user to check link themselves.
        """
        agenda_url = item.css("td")[2].css("a::attr(href)").get()
        return "Check Agenda for start time." if agenda_url else ""

    def _parse_links(self, response, item):
        """Parse or generate links like Agenda or Video links."""
        output = []

        title = item.css("a::text").get()

        # find URL based on link title
        if title and "Agenda" in title:
            link_url = item.css("a::attr(href)").get()
            full_url = urljoin(response.url, link_url)
            output.append({"title": "Agenda", "href": full_url})
        elif title and "Video" in title:
            link_url = item.css("a::attr(onclick)").get().split("'")[1]
            full_url = urljoin(response.url, link_url)
            output.append({"title": "Video", "href": full_url})

        return output
