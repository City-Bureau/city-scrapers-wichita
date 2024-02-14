from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityBbcSpider(WichitaCityMixin):
    name = "wic_city_bbc"
    agency = "Wichita City - Board of Bids & Contracts"
    cid = "77"
