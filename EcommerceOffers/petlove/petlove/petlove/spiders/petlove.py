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
                link=self.CATEGORIES_URL(specie=specie, category=category, page=str(page))
                start_urls.append(link)

        # Create CloudScraper Instance -> Chrome browser // Windows OS // Desktop
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'ios',
                'desktop': False,
                'mobile': True,
            }
        )

        for url in start_urls:
            response = scraper.get(url, headers=self.HEADERS)
            yield scrapy.Request(
                url=self.DUMMY_URL,
                callback=self.parse,
                dont_filter=True,
                meta={'response': response, 'specie': specie, 'category': category, 'page': page}
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

        for offer in offers_list:
            items['collected_at'] = datetime.today().strftime('%Y-%m-%d')
            items['source'] = "Petlove"
            items['specie'] = specie.capitalize() ######################### BROKEN
            items['category'] = category.split("/")[1].replace("-", " ").title() ######################### BROKEN
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

            # offer['details']
            # offer['extras']
            skus = offer.get("extras_skus", [])
            for sku in skus:
                if sku.get("sku", "") == items['sku']:
                    items['status'] = sku.get("properties", "").get("status", "").capitalize()

            # Send items
            yield items

            # Se a offerta tiver multiplas skus
            #if offer.get("multiple_skus", ""):
            # if offer.get("hasMultipleVariants", ""):
            #     items = PetloveItem()
            #     #offer.get("link", "") + "?sku=" + items['sku'] #OK
            #     pass

        # Pagination
        # next_page = page + 1
        # url = self.CATEGORIES_API(specie=specie, category=category, page=next_page)
        # meta={'specie': specie, 'category': category, 'page': next_page}
        # yield response.follow(url, callback=self.parse, meta=meta)