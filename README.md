# USP-MBA-DSA-TCC

### Monitoramento de preços do e-commerce pet com técnicas de raspagem de dados
Objetivo: Observar a eficiência das
técnicas de raspagem de dados no monitoramento de preços de centenas de produtos em
múltiplas lojas do comércio eletrônico “pet” brasileiro
<br>

Metodologia: Coleta de preços de três sites do e-commerce usando spiders desenvolvidas em Python (Scrapy), dados armazenados em Google Big Query, script de alerta de preços (email) e dashboard desenvolvido em Power Bi.

![alt text](https://images.hindustantimes.com/img/2022/02/23/1600x900/happy_pet_1645615655162_1645615663336.jpg)

### Instalando as bibliotecas do projeto
```
pip install -r requirements.txt
```

### Considerações
As spiders necessitam de uma chave json da conta de serviço GCP para armazenagem dos items coletados no banco de dados.