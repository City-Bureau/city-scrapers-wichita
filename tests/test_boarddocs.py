from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from scrapy import Selector
from scrapy.settings import Settings

from city_scrapers.mixins.boarddocs import BoardDocsMixin


class TestBoardDocsMixin:
    @pytest.fixture
    def boarddocs_spider(self):
        # Setup a basic instance of the mixin
        # Ensure the required static vars are set
        class TestSpider(BoardDocsMixin):
            name = "test_spider"
            boarddocs_slug = "test_slug"
            boarddocs_committee_id = "test_committee_id"
            timezone = "America/Chicago"

        spider = TestSpider()
        spider.settings = Settings()
        return spider

    def test_azure_setup(self, boarddocs_spider):
        # Test that the Azure client is setup when the required settings are set
        boarddocs_spider.settings.set("AZURE_ACCOUNT_NAME", "testaccount")
        boarddocs_spider.settings.set("AZURE_ACCOUNT_KEY", "testkey")
        boarddocs_spider.settings.set("AZURE_CONTAINER", "testcontainer")
        boarddocs_spider.setup_azure_client()
        assert boarddocs_spider.container_client is not None

    def test_azure_setup_raises_error(self, boarddocs_spider):
        # Test that an error is raised if the required settings are not set
        boarddocs_spider.settings.set("AZURE_ACCOUNT_NAME", "testaccount")
        boarddocs_spider.settings.set("AZURE_ACCOUNT_KEY", None)
        boarddocs_spider.settings.set("AZURE_CONTAINER", "testcontainer")
        with pytest.raises(KeyError):
            boarddocs_spider.setup_azure_client()

    def test_gen_random_int(self, boarddocs_spider):
        # Test if gen_random_int generates a number within the expected range
        random_int = boarddocs_spider.gen_random_int()
        assert 10**14 <= random_int < 10**15

    def test_get_clean_meetings(self, boarddocs_spider):
        # Mocking data to test the cleaning process
        mock_data = [
            {"numberdate": "20230101", "unique": "1"},  # More than 2 months ago
            {"numberdate": datetime.now().strftime("%Y%m%d"), "unique": "2"},  # Today
            {},  # Empty item
        ]
        result = boarddocs_spider._get_clean_meetings(mock_data)
        assert len(result) == 1  # Only one item should pass the filter
        assert result[0]["unique"] == "2"  # Ensure the correct item is retained

    def test_parse_start_with_time(self, boarddocs_spider):
        # Mocking response and start_date to test _parse_start
        start_date = datetime.now().date()
        response = MagicMock()
        response.css.return_value.get.return_value = "10:00 AM │ Some description"

        parsed_start = boarddocs_spider._parse_start(response, start_date)
        assert parsed_start.hour == 10 and parsed_start.minute == 0

    def test_parse_start_without_time(self, boarddocs_spider):
        # Test parsing when no time is provided in the description
        start_date = datetime.now().date()
        response = MagicMock()
        response.css.return_value.get.return_value = "Some description without time"

        parsed_start = boarddocs_spider._parse_start(response, start_date)
        assert parsed_start.hour == 0 and parsed_start.minute == 0

    def test_parse_title(self, boarddocs_spider):
        # Mocking response to test _parse_title
        response = MagicMock()
        expected_title = "Test Meeting Title"
        response.css.return_value.get.return_value = expected_title

        title = boarddocs_spider._parse_title(response)
        assert (
            title == expected_title
        ), "The parsed title does not match the expected value."

    def test_parse_description(self, boarddocs_spider):
        # Mocking response to test _parse_description, including cleaning
        # HTML tags and normalizing whitespace
        response = MagicMock()
        response.css.return_value.getall.return_value = [
            "Description with  ",
            "  multiple spaces and line breaks  ",
        ]

        description = boarddocs_spider._parse_description(response)
        assert (
            description == "Description with multiple spaces and line breaks"
        ), "The parsed description does not match the expected cleaned and normalized value."  # noqa

    def test_mixin_initialization_requires_vars(self):
        # Testing that the mixin raises NotImplementedError if required
        # static vars are not defined
        with pytest.raises(NotImplementedError) as exc_info:

            class InvalidSpider(BoardDocsMixin):
                pass  # Missing required vars

        assert "must define the following static variable(s)" in str(
            exc_info.value
        ), "Mixin should raise NotImplementedError for missing required static variables."  # noqa

    def test_get_clean_meetings_future_date(self, boarddocs_spider):
        # Testing _get_clean_meetings with a future date to ensure it's included
        future_date = (datetime.now() + timedelta(days=60)).strftime("%Y%m%d")
        mock_data = [{"numberdate": future_date, "unique": "future_meeting"}]

        result = boarddocs_spider._get_clean_meetings(mock_data)
        assert (
            len(result) == 1
        ), "Future meeting should be included in the cleaned data."
        assert (
            result[0]["unique"] == "future_meeting"
        ), "The unique identifier of the future meeting does not match."

    def test_convert_relative_urls(self, boarddocs_spider):
        # Testing that relative URLs are converted to absolute URLs
        html_content = """
        <h1>some content</h1>
        <a href="/relative-url">Some relative URL</a>
        <p>Some more content</p>
        <a href="http://absolute-url.com">Some absolute URL</a>
        <img src="/relative-image.jpg" />
        """
        new_html_content = boarddocs_spider._convert_relative_urls(html_content)
        sel = Selector(text=new_html_content)
        # First a tag's URL relative url should be absolute
        assert sel.css("a::attr(href)").get() == "https://go.boarddocs.com/relative-url"
        # Second a tag's URL should not be modified
        assert sel.css("a::attr(href)").getall()[1] == "http://absolute-url.com"
        # img tag's src should be absolute
        assert (
            sel.css("img::attr(src)").get()
            == "https://go.boarddocs.com/relative-image.jpg"
        )
