# TechStore — Transformation Report

## Tables produites

| Table | Lignes | Colonnes | Clé primaire | Clés étrangères |
|---|---:|---:|---|---|
| `dim_customer` | 24,999 | 6 | `customer_id` | — |
| `dim_supplier` | 60 | 3 | `supplier_id` | — |
| `dim_product` | 600 | 7 | `product_id` | supplier_id → dim_supplier |
| `dim_employee` | 350 | 3 | `employee_id` | — |
| `dim_store` | 31 | 6 | `store_id` | — |
| `dim_warehouse` | 31 | 2 | `warehouse_id` | store_id → dim_store |
| `dim_date` | 1,854 | 7 | `date_key` | — |
| `fact_sales` | 320,000 | 27 | `sale_id` | customer_id, product_id, employee_id, store_id, warehouse_id, sale_date_key, delivery_date_key |
| `fact_returns` | 16,192 | 4 | `sale_id` | sale_id → fact_sales; return_date_key → dim_date |
| `fact_payments` | 320,000 | 5 | `sale_id` | sale_id → fact_sales |
| `fact_inventory` | 320,000 | 6 | `sale_id` | sale_id → fact_sales; product_id → dim_product; warehouse_id → dim_warehouse |

## Grain

- `fact_sales` : une ligne par transaction (`sale_id`).
- `fact_returns` : une ligne par transaction retournée.
- `fact_payments` : une ligne de paiement par transaction ; aucune clé de paiement distincte n’existe dans la source.
- `fact_inventory` : un mouvement/état de stock par transaction, produit et entrepôt.

## Affectation des colonnes

- Client : identité et segmentation dans `dim_customer`; `customer_age` reste dans `fact_sales`, car il varie dans le temps.
- Produit et fournisseur : descriptifs dans leurs dimensions, avec `supplier_id` porté par `dim_product`.
- Magasin, employé et entrepôt : descriptifs dans les dimensions; l’entrepôt est relié de façon univoque au magasin.
- Dates : `sale_date`, `delivery_date` et `return_date` deviennent des clés vers `dim_date`; les attributs calendrier Silver ne sont pas recopiés dans les faits.
- Paiement : méthode, statut, devise et montant net dans `fact_payments`.
- Retour : motif, date et remboursement dans `fact_returns` uniquement.
- Stock : stocks avant/après et quantité vendue dans `fact_inventory` uniquement.

## Colonnes non recopiées ou déplacées

- Aucune colonne Silver n’est abandonnée sans justification : chaque champ est placé dans une dimension, un fait, ou est reconstitué depuis `dim_date`.
- `sale_year`, `sale_month`, `sale_day`, `sale_quarter` et `sale_weekday` ne sont pas recopiés : ils sont calculés une seule fois dans `dim_date`.
- Les attributs client, produit, fournisseur, magasin et employé ne sont pas répétés dans les faits : seules leurs clés y sont conservées.
- Les champs de retour, paiement et stock vivent exclusivement dans leurs tables de faits spécialisées; `is_returned` reste dans `fact_sales` comme indicateur analytique.

## Contrôles de qualité

- Statut global : **PASS**

### Primary Key Issues

- dim_customer: 0
- dim_product: 0
- dim_supplier: 0
- dim_employee: 0
- dim_store: 0
- dim_warehouse: 0
- dim_date: 0
- fact_sales: 0
- fact_returns: 0
- fact_payments: 0
- fact_inventory: 0

### Foreign Key Issues

- dim_product.supplier_id -> dim_supplier: 0
- dim_warehouse.store_id -> dim_store: 0
- fact_sales.customer_id -> dim_customer: 0
- fact_sales.product_id -> dim_product: 0
- fact_sales.employee_id -> dim_employee: 0
- fact_sales.store_id -> dim_store: 0
- fact_sales.warehouse_id -> dim_warehouse: 0
- fact_sales.sale_date_key -> dim_date: 0
- fact_sales.delivery_date_key -> dim_date: 0
- fact_returns.sale_id -> fact_sales: 0
- fact_returns.return_date_key -> dim_date: 0
- fact_payments.sale_id -> fact_sales: 0
- fact_inventory.sale_id -> fact_sales: 0
- fact_inventory.product_id -> dim_product: 0
- fact_inventory.warehouse_id -> dim_warehouse: 0

### Financial Issues

- gross_amount: 0
- discount_amount: 0
- net_amount: 0
- total_cost: 0
- margin_amount: 0

### Quantity Issues

- sales_quantity_missing: 0
- sales_quantity_non_positive: 0
- inventory_quantity_mismatch: 0
- inventory_stock_arithmetic: 0

### Date Issues

- date_key_missing: 0
- date_key_format_issues: 0
- date_key_value_mismatch: 0
- fact_date_key_missing: 0

### Return Issues

- returned_flag_mismatch: 0
- return_date_missing: 0
- refund_above_net_amount: 0

### Payment Issues

- payment_amount_mismatch: 0
- payment_status_missing: 0

### Inventory Issues

- inventory_sale_alignment: 0
- negative_stock: 0
- stock_value_missing: 0

### Completeness Issues

- fact_sales_row_difference_vs_silver: 0
- payment_row_difference_vs_sales: 0
- inventory_row_difference_vs_sales: 0
- returns_not_matching_returned_sales: 0

## Problèmes rencontrés

- Aucun conflit d’attributs pour les dimensions créées.
- L’âge client n’est pas placé dans `dim_customer` afin d’éviter une duplication temporelle; il est conservé au grain de vente.
