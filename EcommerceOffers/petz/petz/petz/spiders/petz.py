import json
import scrapy

from datetime import datetime
from ..items import PetzItem
from scrapy.http import Request

# cd USP-MBA-DSA-TCC/EcommerceOffers/petz/petz
# scrapy crawl petz


class PetzSpider(scrapy.Spider):
    name = 'petz'
    allowed_domains = ['petz.com.br']

    CATEGORIES_API = (
        "https://www.petz.com.br/{specie}/{category}?sort=5&page={page}"
    ).format

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
                    url=self.CATEGORIES_API(specie=specie, category=category, page=str(page)),
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

        offers_xpath = (
            "//section[@id='listProductsShowcase']"
            "//li[@class='card-product card-product-showcase']"
        )

        # End if the page does not contains any offer
        offers_list = response.xpath(offers_xpath)
        if not offers_list or len(offers_list) == 1:
            print("\n","\n", ">>>>> No offer found: ", response, "\n","\n")
            return

        for offer in offers_list:
            json_xpath = "./textarea[@class='jsonGa']/text()"
            json_data = json.loads(offer.xpath(json_xpath).get().strip())

            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Petz"
            items['specie'] = specie.capitalize()
            items['category'] = category.split("/")[1].replace("-", " ").title()

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
        next_page = page + 1
        url = self.CATEGORIES_API(specie=specie, category=category, page=next_page)
        meta={'specie': specie, 'category': category, 'page': next_page}
        yield response.follow(url, callback=self.parse, meta=meta)
