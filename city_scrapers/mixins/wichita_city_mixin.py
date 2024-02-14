import re
from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class WichitaCityMixin(CityScrapersSpider):
    """
    This class is designed to scrape data from the City of Wichita government website.
    Boards and committees are identified by a unique 'cid' value in the URL.

    To use this mixin, create a new spider class that inherits from both this mixin.
    The new spider should have a 'cid' attribute defined.
    """

    name = "wic_apc"
    agency = "Wichita Advance Plans Committee"
    timezone = "America/Chicago"
    base_url = "https://www.wichita.gov"
    links = [{"href": "https://www.wichita.gov/agendacenter", "title": "Agenda Center"}]

    def start_requests(self):
        """Generate request using an URL derived from base url,
        cid (agency identifier) and a range based on the date
        one month prior and six months ahead of the current date."""
        now = datetime.now()
        start_date = (now - relativedelta(months=1)).replace(day=1)
        start_date_str = start_date.strftime("%m/%d/%Y")
        end_date = (now + relativedelta(months=6)).replace(day=1)
        end_date_str = end_date.strftime("%m/%d/%Y")

        # Generate URL
        calendar_url = f"{self.base_url}/calendar.aspx?Keywords=&startDate={start_date_str}&enddate={end_date_str}&CID={self.cid}&showPastEvents=true"  # noqa
        yield scrapy.Request(calendar_url, self.parse)

    def parse(self, response):
        """
        Parse the retrieved HTML, loop over the meeting, and parse the
        detail page for each one.
        """
        selector = f"#CID{self.cid} > ol > li"
        for item in response.css(selector):
            event_query_string = item.css("h3 a::attr(href)").get()
            yield response.follow(event_query_string, self._parse_detail)

    def _parse_detail(self, item):
        title = self._parse_title(item)
        meeting = Meeting(
            title=title,
            description=self._parse_description(item),
            classification=self._parse_classification(title),
            start=self._parse_start(item),
            end=self._parse_end(item),
            all_day=False,
            time_notes="",
            location=self._parse_location(item),
            links=self.links,
            source=item.url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, item):
        """Extracts the event title."""
        return (
            item.css(
                "h2#ctl00_ctl00_MainContent_ModuleContent_ctl00_ctl04_eventTitle::text"
            )
            .get()
            .strip()
        )

    def _parse_description(self, item):
        """Extracts and cleans the HTML to return only text,
        including the original URLs in the text, while removing any
        hidden or non-printable characters."""
        description_sel = item.css("div[itemprop='description']")
        description_texts = []

        # Extract text nodes
        for text_node in description_sel.css("::text").getall():
            cleaned_text = re.sub(
                r"\s+", " ", text_node
            ).strip()  # Replace multiple whitespaces with a single space
            # Check if text is not empty after cleaning
            if cleaned_text:
                description_texts.append(cleaned_text)

        # Extract and format links
        for a_tag in description_sel.css("a"):
            text = a_tag.css("::text").get(default="").strip()
            href = a_tag.css("::attr(href)").get(default="").strip()
            if text and href:
                description_texts.append(f"{text}({href})")

        # Join all parts and strip leading/trailing whitespace
        description = " ".join(description_texts).strip()

        # Remove hidden/non-printable characters
        description = re.sub(r"[^\x20-\x7E]+", "", description)
        return description

    def _parse_classification(self, title):
        """Parse or generate classification from allowed options."""
        if not title:
            return NOT_CLASSIFIED
        elif "board" in title.lower():
            return BOARD
        elif "committee" in title.lower():
            return COMMITTEE
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, response):
        """Extracts the start datetime as a naive datetime object.
        Some events have a dash in the time, indicating start and end times
        """
        date_str = (
            response.css(
                "div#ctl00_ctl00_MainContent_ModuleContent_ctl00_ctl04_dateDiv::text"
            )
            .get()
            .strip()
        )
        time_sel = response.css(
            "div#ctl00_ctl00_MainContent_ModuleContent_ctl00_ctl04_time .specificDetailItem::text"  # noqa
        ).get()
        has_dash = " - " in time_sel
        if has_dash:
            time_str = time_sel.strip().split(" - ")[0]
        else:
            time_str = time_sel.strip()
        datetime_str = f"{date_str} {time_str}"
        return parse(datetime_str)

    def _parse_end(self, response):
        """Extracts the end datetime as a naive datetime object."""
        date_str = (
            response.css(
                "div#ctl00_ctl00_MainContent_ModuleContent_ctl00_ctl04_dateDiv::text"
            )
            .get()
            .strip()
        )
        time_sel = response.css(
            "div#ctl00_ctl00_MainContent_ModuleContent_ctl00_ctl04_time .specificDetailItem::text"  # noqa
        ).get()
        has_dash = " - " in time_sel
        if has_dash:
            time_str = time_sel.strip().split(" - ")[1]
            datetime_str = f"{date_str} {time_str}"
            return parse(datetime_str)
        return None

    def _parse_location(self, item):
        """Extracts the event address and formats it"""
        name = (
            item.css(".specificDetailItem div[itemprop='name']::text")
            .get(default="")
            .strip()
        )
        street = (
            item.css(".specificDetailItem span[itemprop='streetAddress']::text")
            .get()
            .strip()
        )
        locality = (
            item.css(".specificDetailItem span[itemprop='addressLocality']::text")
            .get()
            .strip()
        )
        postal_code = (
            item.css(".specificDetailItem span[itemprop='postalCode']::text")
            .get()
            .strip()
        )
        region = (
            item.css(".specificDetailItem span[itemprop='addressRegion']::text")
            .get()
            .strip()
        )
        return {
            "name": name,
            "address": f"{street}, {locality}, {region} {postal_code}",
        }
