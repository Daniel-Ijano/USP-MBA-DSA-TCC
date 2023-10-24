import scrapy
from ..items import InvestingComItem

# cd USP-MBA-DSA-TCC/News/investing_com/investing_com

class InvestingcomSpider(scrapy.Spider):
    name = 'investingcom'
    page = 1
    source_url = "https://br.investing.com"
    category_economia = "economy"
    category_mercados = "stock-market-news"
    category_moeda = "forex-news"
    category_politica = "politics"
    BASE_URL = "https://br.investing.com/news/{category}/{page}".format

    start_urls = [
        BASE_URL(category=category_economia, page=str(page)),
        BASE_URL(category=category_mercados, page=str(page)),
        BASE_URL(category=category_moeda, page=str(page)),
        BASE_URL(category=category_politica, page=str(page))
        ]

    def parse(self, response):
        items = InvestingComItem()

        category = response.xpath("//h1[@class='float_lang_base_1 relativeAttr']/text()").get().replace('Notícias sobre ', '').replace('\t', '')
        news_list = response.xpath("//div[@class='largeTitle']/article[@class='js-article-item articleItem   ']")

        # End spider if the page does not contains any news
        if not news_list:
            print("\n","\n", ">>>>> No news found: ", response, "\n","\n")
            return

        # Iterating one at a time
        for news in news_list[:1]:
            source = "Investing.com"
            section = category
            publication = news.xpath(".//span[@class='articleDetails']/span[@class ='date']/text()").get() #00000000000000000000000000000000000000000000000000000000000000
            title = news.xpath(".//div[@class='textDiv']/a/@title").get()
            summary = news.xpath(".//div[@class='textDiv']/p/text()").get()
            url = self.source_url + news.xpath(".//div[@class='textDiv']/a/@href").get()

            # Send items
            items['source'] = source
            items['section'] = section
            items['publication'] = publication
            items['title'] = title
            items['summary'] = summary
            items['url'] = url
            yield items

            import ipdb; ipdb.set_trace()

        # Pagination
        self.page += 1
        next_page = self.BASE_URL(category = category.lower(), page=self.page)
        yield response.follow(next_page, callback=self.parse)


# NEXT:
# 1- Parse date******
# 2- Ver se irá adicionar mais categorias
# 3- Arrumar a coleta da data