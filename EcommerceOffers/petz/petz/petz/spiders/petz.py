import json
import requests
import scrapy
import time

from datetime import datetime
from ..items import PetzItem
from lxml import html
from scrapy.http import Request

# cd USP-MBA-DSA-TCC/EcommerceOffers/petz/petz
# scrapy crawl petz


class PetzSpider(scrapy.Spider):
    name = 'petz'
    allowed_domains = ['petz.com.br']

    CATEGORIES_URL = (
        "https://www.petz.com.br/{specie}/{category}?sort=5&page={page}"
    ).format

    VARIANT_API = (
        "https://www.petz.com.br/sendAnalyticsProductViewVariations_Loja.html"
        "?produtoId={product_id}"
    ).format

    XPATHS = {
        "json_data": "./textarea[@class='jsonGa']/text()",
        "offers_list": (
            "//section[@id='listProductsShowcase']"
            "//li[@class='card-product card-product-showcase']"
        ),
        "product_id": "//meta[@itemprop='sku']/@content",
        "rating": (
            "//div[@itemprop='aggregateRating']"
            "//span[@itemprop='ratingValue']/text()"
        ),
        "variants": "//div[@class='variacao-item']/@data-idvariacao"
    }

    def start_requests(self):
        page = 1

        # Species
        species = ["gato", "cachorro"]

        # Categories
        categories = ["racao/racao-seca", "racao/racao-umida"]

        start_urls = []
        for specie in species:
            for category in categories:
                req = Request(
                    url=self.CATEGORIES_URL(specie=specie, category=category, page=str(page)),
                    meta={'specie': specie, 'category': category, 'page': page},
                    callback=self.parse
                )
                start_urls.append(req)
        return start_urls

    def parse(self, response):
        items = PetzItem()
        specie = response.meta.get('specie')
        category = response.meta.get('category')
        page = response.meta.get('page')

        # End if the page does not contains any offer
        offers_list = response.xpath(self.XPATHS["offers_list"])
        if not offers_list or len(offers_list) == 1:
            print("\n", "\n", ">>>>> No offer found: ", response, "\n", "\n")
            return

        for offer in offers_list:
            json_data = json.loads(offer.xpath(self.XPATHS["json_data"]).get().strip())

            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Petz"
            items['specie'] = specie.capitalize()
            items['category'] = category.split("/")[1].replace("-", " ").title()

            items['brand'] = json_data.get("brand", "")
            items['url'] = "https://www.petz.com.br" + offer.xpath("./a/@href").get()

            time.sleep(1)
            offer_response = requests.get(items['url'], timeout=2)
            parsed_response = html.fromstring(offer_response.text)
            rating = parsed_response.xpath(self.XPATHS["rating"])
            product_id = parsed_response.xpath(self.XPATHS["product_id"])
            variants = parsed_response.xpath(self.XPATHS["variants"])

            if not variants:
                variants = product_id

            for variant in variants:
                variant_response = requests.get(self.VARIANT_API(product_id=variant))
                variant_json = variant_response.json()

                # Getting items data
                status = variant_json.get("available", None)
                items['status'] = "Disponível" if status else "Indisponível"

                sku = variant_json.get("sku", None)
                items['sku'] = sku if sku else variant_json.get("product_id", None)

                items['pkg_size'] = variant_json.get("variant", None)
                items['rating'] = float(rating[0]) if rating else None

                items['title'] = variant_json.get("name", None)
                items['description'] = items['title']
                items['regular_price'] = float(variant_json.get("price", 0))
                items['sub_price'] = round(items['regular_price'] * 0.9, 2)
                items['qty'] = None

                # Send items
                yield items

        # Pagination
        next_page = page + 1
        url = self.CATEGORIES_URL(specie=specie, category=category, page=next_page)
        meta = {'specie': specie, 'category': category, 'page': next_page}
        yield response.follow(url, callback=self.parse, meta=meta)
