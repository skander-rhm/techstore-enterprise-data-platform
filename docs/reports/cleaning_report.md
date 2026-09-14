# TechStore — Cleaning Report

- Exécuté (UTC) : 2026-09-08T11:27:18.829264+00:00
- Source RAW (lecture seule) : `data/raw/techstore_dataset.csv`
- Lignes avant nettoyage : 320,000
- Lignes après nettoyage : 320,000

## Corrections appliquées

- text_values_normalized : 0
- invalid_sale_date_converted_to_null : 0
- invalid_delivery_date_converted_to_null : 0
- invalid_return_date_converted_to_null : 0
- exact_duplicate_rows_removed : 0
- duplicate_sale_ids_removed : 0
- invalid_customer_ages_converted_to_null : 0
- customer_ages_imputed : 3,129
- negative_shipping_costs_converted_to_null : 0
- shipping_costs_imputed : 3,248
- gross_amount_recalculated : 0
- discount_amount_recalculated : 0
- net_amount_recalculated : 0
- total_cost_recalculated : 0
- margin_amount_recalculated : 0
- margin_pct_recalculated : 0

## Contrôles de qualité Silver

- Statut global : **PASS**

### Required Field Missing

- sale_id: 0
- sale_date: 0
- store_id: 0
- customer_id: 0
- product_id: 0
- quantity: 0
- net_amount: 0

### Invalid Identifiers

- sale_id: 0
- store_id: 0
- employee_id: 0
- customer_id: 0
- product_id: 0
- supplier_id: 0
- warehouse_id: 0

### Date Issues

- delivery_before_sale: 0
- return_before_sale: 0
- sale_year_mismatch: 0
- sale_month_mismatch: 0
- sale_day_mismatch: 0

### Business Rule Issues

- non_positive_quantity: 0
- negative_unit_price_or_cost: 0
- discount_outside_0_1: 0
- negative_shipping_cost: 0
- customer_age_outside_16_100: 0
- negative_stock: 0
- stock_mismatch: 0
- returned_without_date: 0
- returned_without_reason: 0
- non_returned_with_return_date: 0
- invalid_return_refund: 0
- score_outside_1_5: 0

### Financial Calculation Issues

- gross_amount: 0
- discount_amount: 0
- net_amount: 0
- total_cost: 0
- margin_amount: 0
- margin_pct: 0

## Décisions métier

- Les champs `return_reason` et `return_date` restent nulls pour les ventes non retournées : c’est une absence métier légitime.
- Les scores de satisfaction absents restent nulls ; aucun score n’est inventé.
- Les âges manquants sont imputés par la médiane globale et signalés par `customer_age_imputed`.
- Les frais de livraison manquants sont imputés par la médiane de leur méthode de livraison et signalés par `shipping_cost_imputed`.
- Les valeurs extrêmes sont contrôlées, mais ne sont pas supprimées automatiquement sans règle métier approuvée.
