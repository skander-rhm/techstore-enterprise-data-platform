# TechStore — Data Dictionary

Source : `data/raw/techstore_dataset.csv`. Cette couche est immuable ; les types ci-dessous décrivent la cible analytique.

| Column | Type cible | Description |
|---|---|---|
| sale_id | string | Identifiant unique de transaction. |
| sale_date | date | Date de vente. |
| sale_year, sale_month, sale_day, sale_quarter, sale_weekday | integer / string | Attributs calendaires dérivés de la vente. |
| store_id, store_name | string | Identifiant et nom du magasin. |
| store_city, store_country, store_region, store_type | string | Localisation et typologie du magasin. |
| employee_id, employee_full_name, employee_role | string | Employé en charge de la vente. |
| customer_id, customer_full_name, customer_email | string | Identité du client. |
| customer_gender, customer_age, customer_city, customer_segment | string / integer | Profil client au moment de la vente. |
| product_id, product_name | string | Identifiant et libellé produit. |
| product_category, product_subcategory, product_brand | string | Classification commerciale produit. |
| product_warranty_months | integer | Durée de garantie en mois. |
| supplier_id, supplier_name, supplier_country | string | Fournisseur du produit. |
| quantity | integer | Quantité vendue. |
| unit_price, unit_cost | decimal | Prix de vente et coût unitaire. |
| discount_pct | decimal | Taux de remise appliqué. |
| gross_amount, discount_amount, net_amount | decimal | Montants brut, remise et net. |
| total_cost, margin_amount, margin_pct | decimal | Coût total, marge et taux de marge. |
| currency | string | Devise de la transaction. |
| payment_method, payment_status | string | Moyen et statut du paiement. |
| sales_channel | string | Canal de vente. |
| delivery_method, shipping_cost, delivery_date | string / decimal / date | Informations de livraison. |
| order_status | string | Statut de la commande. |
| is_returned | boolean | Indicateur de retour. |
| return_reason, return_date, refund_amount | string / date / decimal | Informations de retour et remboursement. |
| warehouse_id | string | Entrepôt associé à la vente. |
| stock_before_sale, stock_after_sale | integer | Stock avant et après transaction. |
| customer_satisfaction_score | decimal | Score de satisfaction client, de 1 à 5. |

## Règles de qualité déjà identifiées

- `sale_id` est unique.
- Les dates de vente, livraison et retour sont au format date ISO attendu.
- Les montants sont des mesures financières à convertir en `DECIMAL` dans la base de données.
- `customer_age`, `shipping_cost` et `customer_satisfaction_score` peuvent être absents.
- `return_reason` et `return_date` sont attendus uniquement lorsqu’une vente est retournée.
