SELECT A., B.user_name, B.Email, C.regular_price, C.sub_price, C.Loja, C.Marca, C.Descricao, C.URL, C.img
FROM `usp-mba-dsa-tcc.ecommerce_offers.tb_dim_alerts` A
LEFT JOIN `usp-mba-dsa-tcc.ecommerce_offers.tb_dim_user` B ON A.User_id=B.user_id
LEFT JOIN `usp-mba-dsa-tcc.ecommerce_offers.vw_dim_offers` C ON A.Product_id=C.offer_id