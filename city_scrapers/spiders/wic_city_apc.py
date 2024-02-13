from city_scrapers_core.constants import COMMITTEE

from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityApcSpider(WichitaCityMixin):
    name = "wic_city_apc"
    agency = "City of Wichita - Advance Plans Committee"
    classification = COMMITTEE
    cid = 68
