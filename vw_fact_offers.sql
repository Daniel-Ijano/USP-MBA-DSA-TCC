SELECT collected_at, SHA256(CONCAT(COALESCE(TRIM(source), ''), COALESCE(TRIM(sku), ''))) AS offer_id, 
rating, regular_price, sub_price, qty, status
FROM `usp-mba-dsa-tcc.ecommerce_offers.pet_food`