import scrapy

from datetime import datetime
from ..items import CobasiItem
from ..support import get_data_json_response

# cd USP-MBA-DSA-TCC/EcommerceOffers/cobasi/cobasi
# scrapy crawl cobasi

class CobasiSpider(scrapy.Spider):
    name = 'cobasi'
    allowed_domains = ['cobasi.com.br']

    CATEGORIES_API = (
        "https://mid-back.cobasi.com.br/catalog/products/categories/{category}?"
        "orderBy=OrderByTopSaleDESC&page={page}&pageSize=50"
    ).format

    page = 1

    # Categories
    cat_cachorro_racao_seca = "cachorro/racao/racao-seca"
    cat_gatos_racao_seca = "gatos/racao/racao-seca"

    start_urls = [
        CATEGORIES_API(category=cat_cachorro_racao_seca, page=str(page)),
        CATEGORIES_API(category=cat_gatos_racao_seca, page=str(page))
    ]

    def parse(self, response):
        items = CobasiItem()
        response_json = get_data_json_response(response)

        # End spider if the page does not contains any offer
        offers_list = response_json.get("products", [])
        if not offers_list:
            print("\n","\n", ">>>>> No offer found: ", response, "\n","\n")
            return

        category = response_json.get("id")

        # Iterating one at a time
        for offer in offers_list:
            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Cobasi"
            items['brand'] = offer.get("brandName", "")
            items['rating'] = float(offer.get("rating", 0))
            items['url'] = offer.get("link", "")
            items['status'] = offer.get("status", "").lower()

            sku = offer.get("reference", "")
            items['sku'] = sku if sku else offer.get("id", "")

            title = offer.get("title", "")
            items['title'] = title if title else offer.get("name", "")

            json_item_key = offer.get("items", [])[0]
            items['description'] = json_item_key.get("completeName", "")
            items['pkg_size'] = json_item_key.get("name", "") # AVALIAR REGEX
            items['regular_price'] = float(json_item_key.get("sellers", [])[0].get("price", 0))
            items['sub_price'] = float(json_item_key.get("sellers", [])[0].get("subscriptionPrice", 0)) #ROUNDED
            items['qty'] = int(json_item_key.get("sellers", [])[0].get("quantity", 0))

            import ipdb; ipdb.set_trace()

            # Send items
            yield items

        # Pagination
        # self.page += 1
        # next_page = self.BASE_URL(category = category, page=self.page)
        # yield response.follow(next_page, callback=self.parse)
