from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityBocsaSpider(WichitaCityMixin):
    name = "wic_city_bocsa"
    agency = "Wichita City - Board of Code Standards & Appeals"
    cid = "34"
