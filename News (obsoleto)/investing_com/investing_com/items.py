# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InvestingComItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    source = scrapy.Field()
    section = scrapy.Field()
    publication = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    url = scrapy.Field()