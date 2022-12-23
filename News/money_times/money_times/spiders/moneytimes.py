import scrapy
from ..items import MoneyTimesItem

# cd USP-MBA-DSA-TCC/News/money_times/money_times

class MoneytimesSpider(scrapy.Spider):
    name = 'moneytimes'
    page = 1
    category_economia = "economia"
    category_mercados = "mercados"
    category_empresas = "empresas"
    category_politica = "politica"
    BASE_URL = "https://www.moneytimes.com.br/{category}/page/{page}/".format
    start_urls = [
        BASE_URL(category=category_economia, page=str(page)),
        BASE_URL(category=category_mercados, page=str(page)),
        BASE_URL(category=category_empresas, page=str(page)),
        BASE_URL(category=category_politica, page=str(page))
        ]

    def parse(self, response):
        items = MoneyTimesItem()

        category = response.xpath("//h1[@class='hotsite-header-logo']/text()").get()
        category = category.replace('\n', '').replace('\t', '').lower()

        news_list = response.xpath("//div[@class='news-item']")

        # End spider if the page does not contains any news
        if not news_list:
            print("\n","\n", ">>>>> No news found: ", response, "\n","\n")
            return

        # Iterating one at a time
        for news in news_list:
            source = "Money Times"
            section = news.xpath(".//div[@class='news-item__category']/a/text()").get()
            publication = news.xpath(".//div[@class='news-item__meta']/span/text()").get()
            title = news.xpath(".//h2[@class='news-item__title']/a/text()").get()
            summary = ""
            url = news.xpath(".//h2[@class='news-item__title']/a/@href").get()

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