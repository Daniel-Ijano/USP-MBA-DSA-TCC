WITH
q_raw_product AS(
  SELECT DISTINCT SHA256(CONCAT(COALESCE(TRIM(source), ''), COALESCE(TRIM(sku), ''))) AS offer_id, * EXCEPT(collected_at, rating, status, regular_price, sub_price, qty),
  ROW_NUMBER() OVER (PARTITION BY COALESCE(TRIM(source), ''), COALESCE(TRIM(sku), '') ORDER BY collected_at DESC ) distinct_offers
  FROM `usp-mba-dsa-tcc.ecommerce_offers.pet_food` 
)

SELECT * EXCEPT(distinct_offers)
FROM q_raw_product
WHERE distinct_offers = 1
ORDER BY source, sku