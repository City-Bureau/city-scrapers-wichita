from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityAhrSpider(WichitaCityMixin):
    name = "wic_city_ahr"
    agency = "City of Wichita - Affordable Housing Review Board"
    cid = 30
