import scrapy
from ..items import ValorEconomicoItem
from ..support import get_data_json_response

# cd USP-MBA-DSA-TCC/News/valor_economico/valor_economico

class ValoreconomicoSpider(scrapy.Spider):
    name = 'valoreconomico'
    page = 1
    hash_financas = "72f0952e-8b6b-4706-b734-07dcaec11919"
    hash_politica = "2a02f1ee-5dba-4ff3-bbf7-76a2d139e1a5"
    URLS_API = "https://falkor-cda.bastian.globo.com/tenants/valor/instances/{category}/posts/page/{page}".format
    
    start_urls = [
        URLS_API(category=hash_financas, page=str(page)),
        URLS_API(category=hash_politica, page=str(page))
        ] 
    
    def parse(self, response):
        # From items.py
        items = ValorEconomicoItem()
        response_json = get_data_json_response(response)

        hash = response_json.get("id")
        json_list = response_json.get("items", [{}])

        # End spider if the page does not contains any news
        if not json_list:
            print("\n","\n", ">>>>> No news found: ", response, "\n","\n")
            return

        # Iterating one at a time
        for news in json_list:
            source = "Valor Econômico"
            section = news.get("content").get("section")
            publication = news.get("publication")
            title = news.get("content").get("title")
            summary = news.get("content").get("summary")
            url = news.get("content").get("url")

            # Send items
            items['source'] = source
            items['section'] = section
            items['publication'] = publication
            items['title'] = title
            items['summary'] = summary
            items['url'] = url
            yield items

        # Pagination
        self.page += 1
        next_page = self.URLS_API(category = hash, page=self.page)
        yield response.follow(next_page, callback=self.parse)


# NEXT:
# 1- Parse date******
# 2- Ver se irá adicionar mais categorias