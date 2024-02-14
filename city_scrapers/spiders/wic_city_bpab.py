from city_scrapers.mixins.wichita_city_mixin import WichitaCityMixin


class WicCityBpabSpider(WichitaCityMixin):
    name = "wic_city_bpab"
    agency = "Wichita City - Bicycle & Pedestrian Advisory Board"
    cid = "32"
