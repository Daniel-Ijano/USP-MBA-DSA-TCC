import scrapy

from ..items import PetzItem

# cd USP-MBA-DSA-TCC/EcommerceOffers/petz/petz
# scrapy crawl petz


class PetzSpider(scrapy.Spider):
    name = 'petz'
    #allowed_domains = ['petz.com.br']
    start_urls = ['http://petz.com.br/']

    def parse(self, response):
        items = PetzItem()
        pass
