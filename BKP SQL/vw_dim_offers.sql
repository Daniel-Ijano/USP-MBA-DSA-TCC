WITH
q_raw_product AS(
  SELECT DISTINCT TO_HEX(SHA256(CONCAT(COALESCE(TRIM(source), ''), COALESCE(TRIM(sku), '')))) AS offer_id, 
  source AS Loja, REGEXP_REPLACE(TRIM(specie), r's$', '') AS Especie, TRIM(category) AS Categoria,
  TRIM(url) AS URL, TRIM(sku) AS SKU, TRIM(title) AS Titulo, TRIM(description) AS Descricao, rating, status, regular_price, sub_price, img,

  CASE WHEN LOWER(brand) LIKE '%br4%' AND LOWER(brand) LIKE '%cats%' THEN "BR4 Cats"
  WHEN LOWER(brand) LIKE '%chronos%' THEN "Chronos Pet"
  WHEN LOWER(brand) LIKE '%ecopet%' THEN "Ecopet Natural"
  WHEN LOWER(REGEXP_REPLACE(NORMALIZE(brand, NFD), r'\pM', '')) LIKE '%equilibrio%' THEN "Equilíbrio"
  WHEN LOWER(REGEXP_REPLACE(NORMALIZE(brand, NFD), r'\pM', '')) LIKE '%formula%' AND LOWER(brand) LIKE '%natural%' THEN "Fórmula Natural"
  WHEN LOWER(brand) LIKE '%golden%' OR LOWER(brand) LIKE '%premier%' THEN "Golden" -- Golden is Premier!
  WHEN LOWER(brand) LIKE '%gran%' AND LOWER(brand) LIKE '%plus%' THEN "Gran Plus"
  WHEN LOWER(brand) LIKE '%hill%' THEN "Hills"
  WHEN LOWER(brand) LIKE '%kite%' AND LOWER(brand) LIKE '%kat%' THEN "KiteKat" 
  WHEN LOWER(brand) LIKE '%live%' AND LOWER(brand) LIKE '%long%' THEN "Live Long"
  WHEN LOWER(REGEXP_REPLACE(NORMALIZE(brand, NFD), r'\pM', '')) LIKE '%lider%' THEN "Líder"
  WHEN LOWER(brand) LIKE '%monello%' THEN "Monello"
  WHEN LOWER(brand) LIKE '%pet%' AND LOWER(REGEXP_REPLACE(NORMALIZE(brand, NFD), r'\pM', '')) LIKE '%delicia%' THEN "Pet Delícia"
  WHEN LOWER(brand) LIKE '%cat%' AND LOWER(brand) LIKE '%chow%' THEN "Cat Chow"
  WHEN LOWER(brand) LIKE '%dog%' AND LOWER(brand) LIKE '%chow%' THEN "Dog Chow"
  WHEN LOWER(brand) LIKE '%excellent%' THEN "Excellent"
  WHEN LOWER(brand) LIKE '%fancy%' AND LOWER(brand) LIKE '%feast%' THEN "Fancy Feast"
  WHEN LOWER(brand) LIKE '%felix%' THEN "Felix"
  WHEN LOWER(brand) LIKE '%friskies%' THEN "Friskies"
  WHEN LOWER(brand) LIKE '%pro%' AND LOWER(brand) LIKE '%plan%' THEN "Pro Plan"
  WHEN LOWER(brand) LIKE '%special%' AND LOWER(brand) LIKE '%cat%' THEN "Special Cat"
  WHEN LOWER(brand) LIKE '%special%' AND LOWER(brand) LIKE '%dog%' THEN "Special Dog"
  WHEN LOWER(brand) LIKE '%xis%' AND LOWER(brand) LIKE '%dog%' THEN "Xis Dog"
  WHEN LOWER(brand) LIKE '%zee%' AND LOWER(brand) LIKE '%dog%' THEN "Zee Dog"
  WHEN LOWER(brand) LIKE '%max%' THEN "Max"
  ELSE brand END AS Marca,

  CASE WHEN LOWER(description) LIKE '%castrad%' THEN "Castrado" 
  WHEN LOWER(description) LIKE '%adult%' THEN "Adulto"
  WHEN LOWER(description) LIKE '%filhot%' OR LOWER(description) LIKE '%junior%' THEN "Filhote"
  WHEN LOWER(REGEXP_REPLACE(NORMALIZE(description, NFD), r'\pM', '')) LIKE '%senior%' OR LOWER(description) LIKE '%idos%' THEN "Sênior"
  WHEN LOWER(description) LIKE '%gastro%' THEN "Gastrointestinal"
  WHEN LOWER(description) LIKE '%hipoaler%' THEN "Hipoalergênica"
  WHEN LOWER(description) LIKE '%obes%' THEN "Obesidade"
  WHEN LOWER(description) LIKE '%osteo%' THEN "Osteoartrite"
  WHEN LOWER(description) LIKE '%renal%' THEN "Renal"
  WHEN LOWER(description) LIKE '%urin%' THEN "Urinária"
  WHEN LOWER(description) LIKE '%recov%' OR LOWER(description) LIKE '%recup%' THEN "Recuperação"
  ELSE NULL END AS Grupo,

  CASE WHEN LOWER(pkg_size) LIKE '%pacote%' THEN REGEXP_EXTRACT(REPLACE(REPLACE(LOWER(pkg_size), 'individuais', ''), ' ', ''), r'(?i)pacotesde([\d,]+kg|[\d,]+g)')
  WHEN LOWER(pkg_size) LIKE '%+%' THEN REGEXP_EXTRACT(REPLACE(LOWER(pkg_size), ' ', ''), r'^([\d,]+kg)')
  WHEN LOWER(pkg_size) LIKE '%leve%' AND LOWER(pkg_size) LIKE '%kg%' THEN REGEXP_EXTRACT(REPLACE(LOWER(pkg_size), ' ', ''), r'leve([\d,]+kg|[\d,]+g)')
  WHEN LOWER(pkg_size) LIKE '%g%' THEN REGEXP_EXTRACT(REPLACE(REPLACE(LOWER(pkg_size), '.', ','), ' ', ''), r'([\d,]+kg|[\d,]+g)')
  WHEN LOWER(pkg_size) LIKE '%unid%' AND LOWER(pkg_size) NOT LIKE '%g%' THEN NULL
  ELSE REPLACE(LOWER(pkg_size), ' ', '') END AS pkg_size,
  
  CASE WHEN LOWER(pkg_size) LIKE '%pacote%' THEN REGEXP_EXTRACT(REPLACE(LOWER(pkg_size), ' ', ''), r'^([\d,]+kg|[\d,]+)')
  WHEN LOWER(pkg_size) LIKE '%leve%' AND LOWER(pkg_size) NOT LIKE '%kg%' THEN REGEXP_EXTRACT(REPLACE(LOWER(pkg_size), ' ', ''), r'leve(\d+)')
  WHEN LOWER(pkg_size) LIKE '%unid%' THEN REGEXP_EXTRACT(REPLACE(LOWER(pkg_size), ' ', ''), r'\d+')
  ELSE '1' END pkg_qty,

  TRIM(REPLACE(REGEXP_EXTRACT(LOWER(description), r'\d+(?:,\d+)?\s*(?:[kK][gG]|g)'), ' ', '')) AS title_pkg_size,
  ROW_NUMBER() OVER (PARTITION BY COALESCE(TRIM(source), ''), COALESCE(TRIM(sku), '') ORDER BY collected_at DESC ) distinct_offers
  FROM `usp-mba-dsa-tcc.ecommerce_offers.tb_pet_food_offers` 
),

q_product_regex AS(
  SELECT *,
  CAST(REPLACE(LOWER(REGEXP_EXTRACT(pkg_size, r'[\d,]+')), ',', '.') AS FLOAT64) AS pkg_value,
  CAST(REPLACE(REGEXP_EXTRACT(LOWER(title_pkg_size), r'\d+(?:,\d+)?'), ',', '.') AS FLOAT64) AS title_pkg_value,
  LOWER(REGEXP_EXTRACT(TRIM(pkg_size), r'[a-z]+')) AS pkg_unit,
  LOWER(REGEXP_EXTRACT(title_pkg_size, r'[^,\d\s]+')) AS title_pkg_unit 
  FROM q_raw_product
  WHERE distinct_offers = 1
),

q_embalagem_norm AS(
  SELECT * EXCEPT(status, pkg_qty, distinct_offers),
  CASE WHEN status = 'Available' THEN 'Disponível'
  WHEN status = 'Unavailable' THEN 'Indisponível'
  ELSE status END status,

  CASE WHEN pkg_qty LIKE '%kg%' AND pkg_unit = 'kg' THEN CAST(REPLACE(REGEXP_EXTRACT(pkg_qty, r'[\d,]+'), ',', '.') AS FLOAT64)/pkg_value
  WHEN pkg_qty LIKE '%kg%' AND pkg_unit = 'g' THEN CAST(REPLACE(REGEXP_EXTRACT(pkg_qty, r'[\d,]+'), ',', '.') AS FLOAT64)/(pkg_value/1000)
  ELSE CAST(pkg_qty AS FLOAT64) END QTD_Oferta,

  CASE WHEN pkg_unit = 'kg' THEN pkg_value
  WHEN pkg_unit = 'g' THEN pkg_value/1000
  WHEN pkg_unit IS NULL AND title_pkg_unit = 'kg' THEN title_pkg_value
  WHEN pkg_unit IS NULL AND title_pkg_unit = 'g' THEN title_pkg_value/1000
  ELSE NULL END AS Embalagem_kg

  FROM q_product_regex

),

q_final_step AS(
  SELECT A.* EXCEPT(pkg_size, title_pkg_size, pkg_value, title_pkg_value, pkg_unit, title_pkg_unit), B.Sabores,
  CASE WHEN Embalagem_kg <1 THEN CONCAT(CAST(Embalagem_kg*1000 AS STRING), 'g')
  WHEN Embalagem_kg >=1 THEN CONCAT(CAST(Embalagem_kg AS STRING), 'Kg')
  ELSE NULL END Embalagem,

  CASE WHEN Embalagem_kg IS NOT NULL AND QTD_Oferta IS NOT NULL THEN ROUND(Embalagem_kg * QTD_Oferta, 3)
  ELSE NULL END Total_Oferta_kg,

  FROM q_embalagem_norm A
  LEFT JOIN `usp-mba-dsa-tcc.ecommerce_offers.tb_sabores` B
  ON A.offer_id=B.offer_id
  ORDER BY Loja, SKU
)

SELECT *, CONCAT(Categoria, ' ', Marca, ' ', Especie, ' ',COALESCE(Grupo, ''), ' ',COALESCE(Sabores, ''), ' ',COALESCE(Embalagem), '') Produto
FROM q_final_step