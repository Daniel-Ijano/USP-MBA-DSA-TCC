# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd

from google.cloud import bigquery
from google.oauth2 import service_account


class PetlovePipeline:

    def create_connection(self):
        # Set the credentials and create the connection
        key_path = "../../../usp-mba-dsa-tcc-4277103d9155.json"

        credentials = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )

        self.client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id,
        )
        return credentials

    def create_table(self):

        table_id = "usp-mba-dsa-tcc.ecommerce_offers.TESTE"
        schema = [
            bigquery.SchemaField("collected_at", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("specie", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("brand", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("rating", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("url", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sku", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("pkg_size", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("regular_price", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("sub_price", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("qty", "INTEGER", mode="REQUIRED"),
        ]

        table = bigquery.Table(table_id, schema=schema)
        table = self.client.create_table(table)

        print(
            "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
        )

    def process_item(self, item, spider):
        self.store_db(item)

    def store_db(self, item):
        # Get the credentials
        credentials = self.create_connection()

        # Convert items into a transposed dataframe
        item_df = pd.DataFrame.from_dict(item, orient='index').T
        item_df.to_gbq(
            credentials=credentials,
            destination_table='ecommerce_offers.TESTE',
            if_exists='append'
        )
