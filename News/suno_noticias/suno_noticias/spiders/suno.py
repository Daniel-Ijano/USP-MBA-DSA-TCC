import scrapy
from unidecode import unidecode
from ..items import SunoNoticiasItem

# cd USP-MBA-DSA-TCC/News/suno_noticias/suno_noticias

class SunoSpider(scrapy.Spider):
    name = 'suno'
    page = 1
    category_economia = "economia"
    category_mercados = "mercado"
    category_empresas = "negocios"
    category_politica = "politica"
    BASE_URL = "https://www.suno.com.br/noticias/{category}/page/{page}/".format
    
    start_urls = [
        BASE_URL(category=category_economia, page=str(page)),
        BASE_URL(category=category_mercados, page=str(page)),
        BASE_URL(category=category_empresas, page=str(page)),
        BASE_URL(category=category_politica, page=str(page))
        ]

    def parse(self, response):
        items = SunoNoticiasItem()

        category = response.xpath("//div[@class='wrapper titlePage']/text()").get().strip()
        news_list = response.xpath("//div[@class='cardsPage__listCard__boxs']")

        # End spider if the page does not contains any news
        if not news_list:
            print("\n","\n", ">>>>> No news found: ", response, "\n","\n")
            return

        # Iterating one at a time
        for news in news_list:
            source = "Suno"
            section = category
            publication = news.xpath(".//div[@class='authorBox__name']/time[@itemprop ='datePublished']/text()").get()
            title = news.xpath(".//h2[@class='content__title']/text()").get()
            summary = ""
            url = news.xpath(".//div[@class='cardsPage__listCard__boxs__content']/a/@href").get()

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
        next_page = self.BASE_URL(category = unidecode(category).lower(), page=self.page)
        yield response.follow(next_page, callback=self.parse)


# NEXT:
# 1- Parse date******
# 2- Ver se irá adicionar mais categorias