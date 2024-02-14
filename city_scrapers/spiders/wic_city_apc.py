from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityApcSpider(WichitaCityMixin):
    name = "wic_city_apc"
    agency = "City of Wichita - Advance Plans Committee"
    cid = 68
