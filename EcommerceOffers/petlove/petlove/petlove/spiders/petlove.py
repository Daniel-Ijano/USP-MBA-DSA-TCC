import scrapy

from datetime import datetime
from ..items import PetloveItem
from scrapy.http import Request


# cd USP-MBA-DSA-TCC/EcommerceOffers/petlove/petlove
# scrapy crawl petlove

class PetloveSpider(scrapy.Spider):
    name = 'petlove'
    #allowed_domains = ['petlove.com.br']

    def start_requests(self):
        headers = {
            #"Accept": "*/*",
            #"Accept-Encoding": "gzip, deflate, br",
            #"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
            "Dnt:": "1",
            "Referer": "https://www.petlove.com.br/",
            "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin"
        }

        CATEGORIES_URL = (
            "https://www.petlove.com.br/{specie}/{category}?results_per_page=36&sort=6&page={page}"
        ).format

        page = 1

        # Species
        species = ["gatos", "cachorro"]

        # Categories
        categories = ["racoes/racao-seca", "racoes/racao-umida"]

        start_urls = []
        for specie in species:
            for category in categories:
                req = Request(
                    url=CATEGORIES_URL(specie=specie, category=category, page=str(page)),
                    meta={'specie': specie, 'category': category},
                    callback=self.parse
                )
                start_urls.append(req)
        import ipdb; ipdb.set_trace()
        return start_urls

        # for url in self.start_urls:
        #     try:
        #         yield scrapy.Request(url, headers=headers, callback=self.parse) #, callback=self.parse
        #     except Exception:
        #         print(f"DEU RUIM")
        #         import ipdb; ipdb.set_trace()

        # url = CATEGORIES_URL(specie="gatos", category="racoes/racao-seca", page=1)
        # yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        items = PetloveItem()

        json_xpath = "//div[@class='content']//script[@type='application/javascript']/text()"
        response_json = response.xpath(json_xpath).get().replace('window.catalogJSON = ', '')
        import ipdb; ipdb.set_trace()
