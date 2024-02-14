from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityBeaSpider(WichitaCityMixin):
    name = "wic_city_bea"
    agency = "Wichita City - Board of Electrical Appeals"
    cid = "35"
