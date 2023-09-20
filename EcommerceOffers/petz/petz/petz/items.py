# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PetzItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collected_at = scrapy.Field()
    source = scrapy.Field()
    specie = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    rating = scrapy.Field()
    url = scrapy.Field()
    status = scrapy.Field()
    sku = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    pkg_size = scrapy.Field()
    regular_price = scrapy.Field()
    sub_price = scrapy.Field()
    qty = scrapy.Field()
    img = scrapy.Field()
