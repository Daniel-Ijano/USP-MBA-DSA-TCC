import cloudscraper
import json
import re
import scrapy

from datetime import datetime
from ..items import PetloveItem
from lxml import html


# cd USP-MBA-DSA-TCC/EcommerceOffers/petlove/petlove
# scrapy crawl petlove

class PetloveSpider(scrapy.Spider):
    name = 'petlove'
    allowed_domains = ['petlove.com.br']

    BASE_URL = "https://www.petlove.com.br"

    CATEGORIES_URL = (
        "https://www.petlove.com.br/{specie}/{category}?results_per_page=36&sort=6&page={page}"
    ).format

    HEADERS = {
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        'User-Agent': (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 '
            '(KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
        )
    }

    def start_requests(self):
        page = 1

        # Species
        species = ["gatos", "cachorro"]

        # Categories
        categories = ["racoes/racao-seca", "racoes/racao-umida"]

        start_urls = []
        for specie in species:
            for category in categories:
                cat_url = self.CATEGORIES_URL(specie=specie, category=category, page=str(page))
                url_meta = {
                    "url": cat_url, "specie": specie, "category": category, "page": page
                }
                start_urls.append(url_meta)

        # Create CloudScraper Instance -> Chrome browser // Windows OS // Desktop
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'ios',
                'desktop': False,
                'mobile': True,
            }
        )

        # Requests using cloudscraper
        for url in start_urls[:1]:
            response = scraper.get(url["url"], headers=self.HEADERS)
            meta={'specie': url["specie"], 'category': url["category"], 'page': url["page"]}
            yield from self.parse(response, meta)

    def parse(self, response, meta):
        # Parsing the response
        parsed_response = html.fromstring(response.content)
        json_xpath = "//div[@class='content']//script[@type='application/javascript']/text()"
        raw_response = parsed_response.xpath(json_xpath)[0].strip().replace('window.catalogJSON = ', '').replace(';\n      window.catalogJSON.pageType = "subcategory";', "")
        response_json = json.loads(raw_response)

        items = PetloveItem()
        specie = meta.get('specie')
        category = meta.get('category')
        page = meta.get('page')

        # End if the page does not contains any offer
        offers_list = response_json.get("produtos", [])


        if not offers_list:
            print("\n","\n", ">>>>> No offer found: ", response.meta.get('response').url, "\n","\n")
            return

        # Create CloudScraper Instance -> Chrome browser // Windows OS // Desktop
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'ios',
                'desktop': False,
                'mobile': True,
            }
        )

        for offer in offers_list[:1]:
            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Petlove"
            items['specie'] = specie.capitalize()
            items['category'] = category.split("/")[1].replace("-", " ").title()
            items['brand'] = offer.get("marca", "")
            items['rating'] = float(offer.get("avaliacao", 0))
            items['sku'] = offer.get("sku", "")
            items['url'] = self.BASE_URL + offer.get("sku_url", "")

            items['regular_price'] = float(offer.get("por", 0))
            items['sub_price'] = float(offer.get("preco_assinante", 0))
            items['qty'] = None
            items['title'] = offer.get("nome", "")
            items['description'] = items['title']

            variants = []
            skus = offer.get("extras_skus", [])
            for sku in skus:
                variant_sku = sku.get("sku", "")
                pkg_size = sku.get("properties", "").get("spec", "")
                status = sku.get("properties", "").get("status", "").capitalize()

                # Get the status of the current sku
                if variant_sku == items['sku']:
                    items['status'] = status
                    items['pkg_size'] = pkg_size

                # Store the variants sku for future use
                elif status == "Available":
                    variant = {"variant_sku": variant_sku, "pkg_size": pkg_size, "status": status}
                    variants.append(variant)

            # Send items
            yield items
            import ipdb; ipdb.set_trace()

            # Offer request for variants using cloudscraper
            #if offer.get("multiple_skus", ""):
            if offer.get("hasMultipleVariants", "") or variants:
                for variant in variants:
                    url = offer.get("link", "") + "?sku=" + variant["variant_sku"]
                    response = scraper.get(url, headers=self.HEADERS)
                    meta = {"variant": variant, "items": items}
                    yield from self.parse_offer(response, meta)

        # Pagination requests using cloudscraper
        next_page = page + 1
        url = self.CATEGORIES_URL(specie=specie, category=category, page=str(next_page))
        response = scraper.get(url, headers=self.HEADERS)
        meta={'specie': specie, 'category': category, 'page': next_page}
        yield from self.parse(response, meta)

    def parse_offer(self, response, meta):
        # Getting variants data
        parsed_response = html.fromstring(response.content.decode("utf-8"))

        items = PetloveItem()
        items = meta["items"]
        items["url"] = response.url
        items["sku"] = meta["variant"]["variant_sku"]
        items["pkg_size"] = meta["variant"]["pkg_size"]

        title = parsed_response.xpath("//title/text()")[0].replace(" | Petlove", "")
        items["title"] =  f"{title} - {items['pkg_size']}"
        items["description"] = items["title"]

        price_xpath =  (
            "//div[@class='product__call-to-action-wrapper']"
            "//button[@datatest-id='{id}']"
            "//span[@class='button__label']/text()"
        ).format

        regular_price = parsed_response.xpath(price_xpath(id="add-to-cart"))[0].strip().replace(".", "")
        items["regular_price"] = float(re.findall(r"\d+,\d+", regular_price)[0].replace(",", "."))

        sub_price = parsed_response.xpath(price_xpath(id="add-to-recurrences"))[0].strip().replace(".", "")
        items["sub_price"] = float(re.findall(r"\d+,\d+", sub_price)[0].replace(",", "."))

        # Send items
        yield items
