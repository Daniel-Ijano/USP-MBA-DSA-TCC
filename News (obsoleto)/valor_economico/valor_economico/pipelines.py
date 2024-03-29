# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
# import mysql.connector
import cx_Oracle


class ValorEconomicoPipeline:
    def __init__(self):
        self.create_connection()
        #self.create_table()

    def create_connection(self):
        # self.conn = mysql.connector.connect(
        #     host='localhost',
        #     user='root',
        #     passwd='1234',
        #     database="news"
        # )

        # Configuration of oracle connection for windows:
        # https://www.youtube.com/watch?v=C9op6I-4WM0
        self.conn = cx_Oracle.connect("admin", "Onlin3#onlin3#", "adbnews_high")
        self.curr = self.conn.cursor()

    def create_table(self):
        # self.curr.execute("""DROP TABLE IF EXISTS tb_news_TEMP""")
        # query = """
        #     CREATE TABLE tb_news_TEMP(
        #     source text
        #     , section text
        #     , publication text
        #     , title text
        #     , body text
        #     , url text
        #     )
        #     """

        query = """
            CREATE TABLE tb_news_TEMP(
            publication_id VARCHAR2 (32) NOT NULL
            , source VARCHAR2 (50) NOT NULL
            , section VARCHAR2 (20) NOT NULL
            , publication VARCHAR2 (50) NOT NULL
            , collected_at VARCHAR2 (50) NOT NULL
            , title VARCHAR2 (500) NOT NULL
            , body VARCHAR2 (10000)
            , url VARCHAR2 (200) NOT NULL
            )
            """
        self.curr.execute(query)

    def process_item(self, item, spider):
        self.store_db(item)
        # return item #Print item

    def store_db(self, item):

        # self.curr.execute(
        #     """
        #     INSERT INTO tb_news_TEMP
        #     VALUES (%s,%s,%s,%s,%s,%s)
        #     """,
        #     (
        #         item["source"],
        #         item["section"],
        #         item["publication"],
        #         item["title"],
        #         item["body"],
        #         item["url"],
        #     ),
        # )

        query = """
            INSERT INTO tb_news_TEMP
            VALUES (:publication_id, :source, :section, :publication, :collected_at, :title, :body, :url)
        """
        #(source, section, publication, title, body, url)
        self.curr.execute(
            query,
            publication_id=item["publication_id"],
            source=item["source"],
            section=item["section"],
            publication=item["publication"],
            collected_at=item["collected_at"],
            title=item["title"],
            body=item["body"],
            url=item["url"],
        )

        self.conn.commit()

    def __del__(self):
        self.curr.close()
        self.conn.close()
