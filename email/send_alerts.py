# Importação das bibliotecas
import logging
import win32com.client as win32
from google.cloud import bigquery
from google.oauth2 import service_account


# Create the connection with Google Cloud
def create_connection():
    # Set the credentials and create the connection
    key_path = "../usp-mba-dsa-tcc-4277103d9155.json"

    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )

    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )
    return client


# Perform a query.
def perform_query(client):
    QUERY = (
        "SELECT * FROM `usp-mba-dsa-tcc.ecommerce_offers.vw_send_alerts` WHERE Status='Active'"
    )
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    df = rows.to_dataframe()
    return df


# Send emails
def send_emails(df):
    outlook = win32.Dispatch('outlook.application')
    for row in df.index:
        if float(df['sub_price'][row]) <= float(df['Target'][row]):

            mail = outlook.CreateItem(0)
            mail.To = df['Email'][row]
            mail.Subject = "Seu alerta de preço foi atingido!"
            mail.HTMLBody = f"""
            <p style="font-family: sans-serif; color: #4c4c4c;">Olá {df['user_name'][row]},<br>O produto que você estava monitorando baixou!!</p>

            <div class="container" style="display: flex; align-items: center; max-width: 500px; background-image:url(https://www.colorhexa.com/ffffff.png)">
                <img class="image" src={df[ 'img'][row]} alt="Imagem do Produto" width=200 height=200>
                <strong><p style="font-family: sans-serif; font-size: 20px; color: #4c4c4c;">{df['Marca'][row]}</p>
                            <p style="font-family: sans-serif; font-size: 16px; color: #4c4c4c;">{df['Descricao'][row]}</p>
                            <p style="font-family: sans-serif; font-size: 24px; color: #4c4c4c;">R${str("{:.2f}".format(df['sub_price'][row])).replace('.', ',')}</p></strong>
            </div>

            <br><strong><a href={df['URL'][row]} style="display: block; text-align: center; background-color: #01878e; padding: 10px; 
                            font-family: sans-serif; font-size: 16px; max-width: 500px; text-decoration: none; color: white;">IR PARA A LOJA</a></strong>
            """
            mail.Send()


# Run
logging.info('Estabelecendo conexão com o Google Cloud')
client = create_connection()

logging.info('Realizando consulta')
df = perform_query(client)

logging.info('Enviando os emails')
send_emails(df)

logging.info('Emails enviados!')
