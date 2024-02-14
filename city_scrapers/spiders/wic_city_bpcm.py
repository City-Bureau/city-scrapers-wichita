from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityBpcmSpider(WichitaCityMixin):
    name = "wic_city_bpcm"
    agency = "Wichita City - Board of Park Commissioners"
    cid = "28"
