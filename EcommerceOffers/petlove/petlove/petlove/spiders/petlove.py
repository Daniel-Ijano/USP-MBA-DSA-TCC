import cloudscraper
import json
import scrapy

from datetime import datetime
from ..items import PetloveItem
from lxml import html
from scrapy.http import Request


# cd USP-MBA-DSA-TCC/EcommerceOffers/petlove/petlove
# scrapy crawl petlove

class PetloveSpider(scrapy.Spider):
    name = 'petlove'
    #allowed_domains = ['petlove.com.br']

    CATEGORIES_URL = (
        "https://www.petlove.com.br/{specie}/{category}?results_per_page=36&sort=6&page={page}"
    ).format

    DUMMY_URL = "https://quotes.toscrape.com/"
    
    BASE_URL = "https://www.petlove.com.br"

    HEADERS = {
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
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
                url_meta = {"url": cat_url, "specie": specie, "category": category, "page": str(page)}
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

        for url in start_urls[:1]:
            response = scraper.get(url["url"], headers=self.HEADERS)
            yield scrapy.Request(
                url=self.DUMMY_URL,
                callback=self.parse,
                dont_filter=True,
                meta={'response': response, 'specie': url["specie"], 'category': url["category"], 'page': url["page"]}
            )

    def parse(self, response):
        # Parsing the response
        parsed_response = html.fromstring(response.meta.get('response').content)
        json_xpath = "//div[@class='content']//script[@type='application/javascript']/text()"
        raw_response = parsed_response.xpath(json_xpath)[0].strip().replace('window.catalogJSON = ', '').replace(';\n      window.catalogJSON.pageType = "subcategory";', "")
        response_json = json.loads(raw_response)

        items = PetloveItem()
        specie = response.meta.get('specie')
        category = response.meta.get('category')
        page = response.meta.get('page')

        # End if the page does not contains any offer
        offers_list = response_json.get("produtos", [])
        if not offers_list:
            print("\n","\n", ">>>>> No offer found: ", response.meta.get('response').url, "\n","\n")
            return

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
            items['pkg_size'] = offer.get("sku_spec", "")
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

                # Store the variants sku for future use
                elif status == "Available":
                    variant = {"variant_sku": variant_sku, "pkg_size": pkg_size, "status": status}
                    variants.append(variant)

            # Send items
            yield items

            # Create CloudScraper Instance -> Chrome browser // Windows OS // Desktop
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'ios',
                    'desktop': False,
                    'mobile': True,
                }
            )

            # Offer request for variants
            #if offer.get("multiple_skus", ""):
            if offer.get("hasMultipleVariants", "") or variants:
                for variant in variants:
                    url = offer.get("link", "") + "?sku=" + variant["variant_sku"]
                    response = scraper.get(url, headers=self.HEADERS)
                    metadados = {"variant": variant, "items": items}
                    yield from self.parse_offer(response, metadados)

        # Pagination
        next_page = page + 1
        url = self.CATEGORIES_URL(specie=specie, category=category, page=str(next_page))
        response = scraper.get(url, headers=self.HEADERS)
        yield scrapy.Request(
            url=self.DUMMY_URL,
            callback=self.parse,
            dont_filter=True,
            meta={'response': response, 'specie': specie, 'category': category, 'page': next_page}
        )

    def parse_offer(self, response, metadados):
        # Getting variants data
        parsed_response = html.fromstring(response.content.decode("utf-8"))

        items = PetloveItem()
        items = metadados["items"]
        items["url"] = response.url
        items["sku"] = metadados["variant"]["variant_sku"]
        items["pkg_size"] = metadados["variant"]["pkg_size"]

        title = parsed_response.xpath("//title/text()")[0].replace(" | Petlove", "")
        items["title"] =  f"{title} - {items['pkg_size']}"
        items["description"] = items["title"]
        import ipdb; ipdb.set_trace()

        # Xpaths #################################################################################################### FALTA AQUI E DEPOIS MELHORAR A DUMMY REQUEST
        items["regular_price"] = None
        items["sub_price"] = None

        # Send items
        # yield items
