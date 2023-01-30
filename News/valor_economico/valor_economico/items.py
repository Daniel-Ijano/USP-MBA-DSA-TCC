# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ValorEconomicoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    publication_id = scrapy.Field()
    source = scrapy.Field()
    section = scrapy.Field()
    publication = scrapy.Field()
    collected_at = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    url = scrapy.Field()
