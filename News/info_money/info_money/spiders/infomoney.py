import scrapy

# cd USP-MBA-DSA-TCC/News/info_money/info_money

class InfomoneySpider(scrapy.Spider):
    name = 'infomoney'
    start_urls = [
        'https://www.infomoney.com.br/politica/',
        'https://www.infomoney.com.br/mercados/',
        'https://www.infomoney.com.br/economia/'
    ]

    def parse(self, response):
        pass
