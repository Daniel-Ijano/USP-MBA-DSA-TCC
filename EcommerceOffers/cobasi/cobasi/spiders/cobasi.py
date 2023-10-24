import scrapy

from datetime import datetime
from ..items import CobasiItem
from scrapy.http import Request
from ..support import get_data_json_response

# cd USP-MBA-DSA-TCC/EcommerceOffers/cobasi/cobasi
# scrapy crawl cobasi

class CobasiSpider(scrapy.Spider):
    name = 'cobasi'
    allowed_domains = ['cobasi.com.br']

    CATEGORIES_API = (
        "https://mid-back.cobasi.com.br/catalog/products/categories/{specie}/{category}?"
        "orderBy=OrderByTopSaleDESC&page={page}&pageSize=50"
    ).format

    def start_requests(self):
        page = 1

        # Species
        species = ["gatos", "cachorro"]

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
        items = CobasiItem()
        specie = response.meta.get('specie')
        category = response.meta.get('category')
        page = response.meta.get('page')
        response_json = get_data_json_response(response)

        # End if the page does not contains any offer
        offers_list = response_json.get("products", [])
        if not offers_list:
            print("\n","\n", ">>>>> No offer found: ", response, "\n","\n")
            return

        for offer in offers_list:
            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Cobasi"
            items['specie'] = specie.capitalize()
            items['category'] = category.split("/")[1].replace("-", " ").title()
            items['brand'] = offer.get("brandName", "")
            items['rating'] = float(offer.get("rating", 0))
            items['url'] = offer.get("link", "")
            items['status'] = offer.get("status", "").capitalize()

            sku = offer.get("reference", "")
            items['sku'] = sku if sku else offer.get("id", "")

            title = offer.get("title", "")
            items['title'] = title if title else offer.get("name", "")

            json_item_key = offer.get("items", [])[0]
            items['description'] = json_item_key.get("completeName", "")
            items['pkg_size'] = json_item_key.get("name", "") #
            items['regular_price'] = float(json_item_key.get("sellers", [])[0].get("price", 0))
            items['sub_price'] = float(json_item_key.get("sellers", [])[0].get("subscriptionPrice", 0))
            items['qty'] = int(json_item_key.get("sellers", [])[0].get("quantity", 0))

            img = json_item_key.get("images", [])[0].get("url", None)
            items['img'] = "https:" + img if img else None

            # Send items
            yield items

        # Pagination
        next_page = page + 1
        url = self.CATEGORIES_API(specie=specie, category=category, page=next_page)
        meta={'specie': specie, 'category': category, 'page': next_page}
        yield response.follow(url, callback=self.parse, meta=meta)
