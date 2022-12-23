# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector

class SunoNoticiasPipeline:
    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database="news"
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS tb_news_TEMP""")
        self.curr.execute("""
            CREATE TABLE tb_news_TEMP(
            source text
            , section text
            , publication text
            , title text
            , summary text
            , url text
            )
            """)

    def process_item(self, item, spider):
        self.store_db(item)
        #return item #Print item

    def store_db(self, item):
        self.curr.execute("""INSERT INTO tb_news_TEMP VALUES (%s,%s,%s,%s,%s,%s)""", (
            item['source'],
            item['section'],
            item['publication'],
            item['title'],
            item['summary'],
            item['url']
        ))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

