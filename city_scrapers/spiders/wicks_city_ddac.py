from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicksCityDDACSpider(WichitaCityMixin):
    name = "wicks_city_ddac"
    agency = "Wichita City - Delano District Advisory Committee"
    cid = "75"