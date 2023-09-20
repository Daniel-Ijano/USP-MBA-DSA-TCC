# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd

from google.cloud import bigquery
from google.oauth2 import service_account


class CobasiPipeline:

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

    def process_item(self, item, spider):
        self.store_db(item)

    def store_db(self, item):
        # Get the credentials
        credentials = self.create_connection()

        # Convert items into a transposed dataframe
        item_df = pd.DataFrame.from_dict(item, orient='index').T
        item_df.to_gbq(
            credentials=credentials,
            destination_table='ecommerce_offers.tb_raw_pet_food',
            if_exists='append'
        )
