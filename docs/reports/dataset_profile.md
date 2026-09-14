# TechStore — Dataset Profiling Report

- Source: `data/raw/techstore_dataset.csv`
- Rows: 320,000
- Columns: 58
- Exact duplicate rows: 0

| Column | Type | Non-null | Missing | Missing % | Distinct | Sample values |
|---|---|---:|---:|---:|---:|---|
| sale_id | str | 320,000 | 0 | 0.00% | 320,000 | TRX0000001, TRX0000002, TRX0000003 |
| sale_date | str | 320,000 | 0 | 0.00% | 1,826 | 2020-06-16, 2020-08-02, 2021-12-14 |
| sale_year | int64 | 320,000 | 0 | 0.00% | 5 | 2020, 2020, 2021 |
| sale_month | int64 | 320,000 | 0 | 0.00% | 12 | 6, 8, 12 |
| sale_day | int64 | 320,000 | 0 | 0.00% | 31 | 16, 2, 14 |
| sale_quarter | int64 | 320,000 | 0 | 0.00% | 4 | 2, 3, 4 |
| sale_weekday | str | 320,000 | 0 | 0.00% | 7 | Tuesday, Sunday, Tuesday |
| store_id | str | 320,000 | 0 | 0.00% | 31 | STR002, STR029, STR027 |
| store_name | str | 320,000 | 0 | 0.00% | 31 | TechStore Lyon, TechStore Abidjan, TechStore New York |
| store_city | str | 320,000 | 0 | 0.00% | 31 | Lyon, Abidjan, New York |
| store_country | str | 320,000 | 0 | 0.00% | 20 | France, Côte d'Ivoire, États-Unis |
| store_region | str | 320,000 | 0 | 0.00% | 4 | Europe, Afrique, Amérique du Nord |
| store_type | str | 320,000 | 0 | 0.00% | 4 | Corner en galerie marchande, Retail Park, Hypermarché high-tech |
| employee_id | str | 320,000 | 0 | 0.00% | 350 | EMP0308, EMP0258, EMP0067 |
| employee_full_name | str | 320,000 | 0 | 0.00% | 280 | Ethan Bouazizi, Lucas Moreau, Enzo Chaabane |
| employee_role | str | 320,000 | 0 | 0.00% | 7 | Vendeur, Manager Magasin, Vendeur Senior |
| customer_id | str | 320,000 | 0 | 0.00% | 24,999 | CUS10656, CUS03585, CUS10249 |
| customer_full_name | str | 320,000 | 0 | 0.00% | 900 | Lina Bernard, Louis Robert, Lucas Lefebvre |
| customer_email | str | 320,000 | 0 | 0.00% | 24,999 | lina.bernard10655@topnet.tn, louis.robert3584@outlook.com, lucas.lefebvre10248@gmail.com |
| customer_gender | str | 320,000 | 0 | 0.00% | 3 | F, F, M |
| customer_age | float64 | 316,871 | 3,129 | 0.98% | 64 | 48.0, 71.0, 54.0 |
| customer_city | str | 320,000 | 0 | 0.00% | 31 | Le Caire, Québec, Genève |
| customer_segment | str | 320,000 | 0 | 0.00% | 4 | Professionnel, Entreprise, Particulier |
| product_id | str | 320,000 | 0 | 0.00% | 600 | PRD0315, PRD0031, PRD0111 |
| product_name | str | 320,000 | 0 | 0.00% | 600 | Samsung Moniteur Gaming 3913, Apple Workstation 4465, HyperX Manette 2014 |
| product_category | str | 320,000 | 0 | 0.00% | 10 | Écrans, Ordinateurs de Bureau, Périphériques |
| product_subcategory | str | 320,000 | 0 | 0.00% | 49 | Moniteur Gaming, Workstation, Manette |
| product_brand | str | 320,000 | 0 | 0.00% | 48 | Samsung, Apple, HyperX |
| product_warranty_months | int64 | 320,000 | 0 | 0.00% | 4 | 24, 12, 12 |
| supplier_id | str | 320,000 | 0 | 0.00% | 60 | SUP014, SUP022, SUP034 |
| supplier_name | str | 320,000 | 0 | 0.00% | 60 | AMD, HyperX, Anker Innovations |
| supplier_country | str | 320,000 | 0 | 0.00% | 8 | Japon, Corée du Sud, Japon |
| quantity | int64 | 320,000 | 0 | 0.00% | 5 | 2, 1, 1 |
| unit_price | float64 | 320,000 | 0 | 0.00% | 598 | 515.53, 564.32, 288.61 |
| unit_cost | float64 | 320,000 | 0 | 0.00% | 598 | 316.43, 370.91, 194.71 |
| discount_pct | float64 | 320,000 | 0 | 0.00% | 6 | 0.1, 0.0, 0.0 |
| gross_amount | float64 | 320,000 | 0 | 0.00% | 2,983 | 1031.06, 564.32, 288.61 |
| discount_amount | float64 | 320,000 | 0 | 0.00% | 7,313 | 103.11, 0.0, 0.0 |
| net_amount | float64 | 320,000 | 0 | 0.00% | 15,323 | 927.95, 564.32, 288.61 |
| total_cost | float64 | 320,000 | 0 | 0.00% | 2,963 | 632.86, 370.91, 194.71 |
| margin_amount | float64 | 320,000 | 0 | 0.00% | 14,406 | 295.09, 193.41, 93.9 |
| margin_pct | float64 | 320,000 | 0 | 0.00% | 568 | 0.318, 0.343, 0.325 |
| currency | str | 320,000 | 0 | 0.00% | 9 | EUR, TND, USD |
| payment_method | str | 320,000 | 0 | 0.00% | 6 | PayPal, Carte Bancaire, Carte Bancaire |
| payment_status | str | 320,000 | 0 | 0.00% | 4 | Payé, Payé, Payé |
| sales_channel | str | 320,000 | 0 | 0.00% | 4 | Magasin Physique, Application Mobile, Magasin Physique |
| delivery_method | str | 320,000 | 0 | 0.00% | 4 | Livraison Standard, Point Relais, Retrait Magasin |
| shipping_cost | float64 | 316,752 | 3,248 | 1.01% | 2,302 | 4.22, 2.34, 0.0 |
| delivery_date | str | 320,000 | 0 | 0.00% | 1,835 | 2020-06-24, 2020-08-11, 2021-12-14 |
| order_status | str | 320,000 | 0 | 0.00% | 4 | Livrée, Livrée, Livrée |
| is_returned | bool | 320,000 | 0 | 0.00% | 2 | False, False, False |
| return_reason | str | 16,192 | 303,808 | 94.94% | 6 | Erreur de commande, Produit endommagé pendant transport, Erreur de commande |
| return_date | str | 16,192 | 303,808 | 94.94% | 1,849 | 2024-03-29, 2022-01-14, 2024-08-22 |
| refund_amount | float64 | 320,000 | 0 | 0.00% | 6,499 | 0.0, 0.0, 0.0 |
| warehouse_id | str | 320,000 | 0 | 0.00% | 31 | WH002, WH029, WH027 |
| stock_before_sale | int64 | 320,000 | 0 | 0.00% | 253 | 152, 9, 7 |
| stock_after_sale | int64 | 320,000 | 0 | 0.00% | 249 | 150, 8, 6 |
| customer_satisfaction_score | float64 | 206,179 | 113,821 | 35.57% | 5 | 5.0, 5.0, 4.0 |
