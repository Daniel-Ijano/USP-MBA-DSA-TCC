import json
import requests
import scrapy

from datetime import datetime
from ..items import PetzItem
from lxml import html
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
        for specie in species[:1]:
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
            items['url'] = "https://www.petz.com.br" + offer.xpath("./a/@href").get()
            status_xpath = "./div/meta[@itemprop='itemCondition']/@content"
            items['status'] = offer.xpath(status_xpath).get()

            variants = offer.xpath("//@product-variations-text").get()
            if variants:
                print("VARIANTS!!")
                import ipdb; ipdb.set_trace()
                offer_response = html.fromstring(requests.get(items['url']).content.decode("utf-8"))
                script_content = offer_response.xpath('//script[contains(., "var chaordicProduct")]//text()')[0].split("};")
                abc = script_content[1].replace("var chaordicProduct = ", "").replace("\r", "").replace("\n", "").replace("\t", "")
                start_index = abc.find('"details": {"')
                end_index = abc.rfind('"extraInfo": {')
                LALALA = abc[:start_index] + abc[end_index:]+"}"
                json_data = json.loads(LALALA).get("product", "")

                # Extract JSON data from the script content
                start_index = script_content.find("var chaordicProduct = {")
                end_index = script_content.rfind("};") #+ 1
                json_data = script_content[start_index:end_index]

                #yield response.follow(url=items['url'], callback=self.parse_offer, meta=meta)
                #yield Request(url=items['url'], callback=self.parse_offer, meta=meta)

            else:
                sku = json_data.get("sku", "")
                items['sku'] = sku if sku else json_data.get("id", "")

                items['title'] = json_data.get("name", "")
                items['regular_price'] = float(json_data.get("price", 0))
                items['sub_price'] = float(json_data.get("priceForSubs", 0))

                items['pkg_size'] = None ################################################################# IMPORTANTE!
                items['rating'] = None
                items['description'] = None
                items['qty'] = None

                # Send items
                yield items

        # Pagination
        next_page = page + 1
        url = self.CATEGORIES_API(specie=specie, category=category, page=next_page)
        meta={'specie': specie, 'category': category, 'page': next_page}
        yield response.follow(url, callback=self.parse, meta=meta)
