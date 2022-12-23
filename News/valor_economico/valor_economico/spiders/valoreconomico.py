import scrapy
from ..items import ValorEconomicoItem
from ..support import get_data_json_response

# cd USP-MBA-DSA-TCC/News/valor_economico/valor_economico

class ValoreconomicoSpider(scrapy.Spider):
    name = 'valoreconomico'
    page = 1
    category_financas = "72f0952e-8b6b-4706-b734-07dcaec11919"
    category_politica = "2a02f1ee-5dba-4ff3-bbf7-76a2d139e1a5"
    BASE_URL = "https://falkor-cda.bastian.globo.com/tenants/valor/instances/{category}/posts/page/{page}".format
    
    start_urls = [
        BASE_URL(category=category_financas, page=str(page)),
        BASE_URL(category=category_politica, page=str(page))
        ] 
    
    def parse(self, response):
        items = ValorEconomicoItem()
        response_json = get_data_json_response(response)

        category = response_json.get("id")
        news_list = response_json.get("items", [{}])

        # End spider if the page does not contains any news
        if not news_list:
            print("\n","\n", ">>>>> No news found: ", response, "\n","\n")
            return

        # Iterating one at a time
        for news in news_list:
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
        next_page = self.BASE_URL(category = category, page=self.page)
        yield response.follow(next_page, callback=self.parse)


# NEXT:
# 1- Parse date******
# 2- Ver se irá adicionar mais categorias