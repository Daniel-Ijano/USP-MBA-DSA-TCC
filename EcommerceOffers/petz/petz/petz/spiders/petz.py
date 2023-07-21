import json
import scrapy

from datetime import datetime
from ..items import PetzItem
from scrapy.http import Request

# cd USP-MBA-DSA-TCC/EcommerceOffers/petz/petz
# scrapy crawl petz


class PetzSpider(scrapy.Spider):
    name = 'petz'
    #allowed_domains = ['petz.com.br']

    def start_requests(self):
        CATEGORIES_API = (
            "https://www.petz.com.br/{specie}/{category}?sort=5&page={page}"
        ).format

        page = 1

        # Species
        species = ["gato", "cachorro"]

        # Categories
        categories = ["racao/racao-seca", "racao/racao-umida"]

        start_urls = []
        for specie in species:
            for category in categories:
                req = Request(
                    url=CATEGORIES_API(specie=specie, category=category, page=str(page)),
                    meta={'specie': specie, 'category': category},
                    callback=self.parse
                )
                start_urls.append(req)
        return start_urls

    def parse(self, response):
        items = PetzItem()

        # RESOLVER PROBLEMA DO SCROLL DOWN PARA CARREGAMENTO DE MAIS PRODUTOS
        # len(products) ANTES x DEPOIS

        offers_xpath = (
            "//section[@id='listProductsShowcase']"
            "//li[@class='card-product card-product-showcase']"
        )
        offers_list = response.xpath(offers_xpath)

        for offer in offers_list:
            json_xpath = "./textarea[@class='jsonGa']/text()"
            json_data = json.loads(offer.xpath(json_xpath).get().strip())

            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Petz"
            items['specie'] = response.meta.get('specie').capitalize()
            items['category'] = response.meta.get('category').split("/")[1].replace("-", " ").title()

            items['brand'] = json_data.get("brand", "")
            items['rating'] = None
            items['url'] = "https://www.petz.com.br" + offer.xpath("./a/@href").get()
            status_xpath = "./div/meta[@itemprop='itemCondition']/@content"
            items['status'] = offer.xpath(status_xpath).get()

            sku = json_data.get("sku", "")
            items['sku'] = sku if sku else json_data.get("id", "")

            items['title'] = json_data.get("name", "")
            items['description'] = None
            items['pkg_size'] = None ################################################################# IMPORTANTE!

            items['regular_price'] = float(json_data.get("price", 0))
            items['sub_price'] = float(json_data.get("priceForSubs", 0))
            items['qty'] = None

            # Send items
            yield items

        # Pagination
        # self.page += 1
        # next_page = self.BASE_URL(category = category, page=self.page)
        # yield response.follow(next_page, callback=self.parse)

        ###################################################### FIX PAGINATION