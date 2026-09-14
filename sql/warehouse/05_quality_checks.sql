SELECT 'fact_sales_row_count' AS check_name,
       CASE WHEN COUNT(*) = 320000 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_sales;

SELECT 'fact_sales_duplicate_sale_id' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM (
    SELECT sale_id
    FROM dw.dw_fact_sales
    GROUP BY sale_id
    HAVING COUNT(*) > 1
) duplicates;

SELECT 'fact_sales_amount_consistency' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_sales
WHERE ABS(gross_amount - quantity * unit_price) > 0.011
   OR ABS(discount_amount - gross_amount * discount_pct) > 0.011
   OR ABS(net_amount - gross_amount + discount_amount) > 0.011
   OR ABS(total_cost - quantity * unit_cost) > 0.011
   OR ABS(margin_amount - net_amount + total_cost) > 0.011;

SELECT 'fact_returns_referential_integrity' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_returns returns
LEFT JOIN dw.dw_fact_sales sales ON sales.sales_key = returns.sales_key
WHERE sales.sales_key IS NULL;

SELECT 'fact_payments_amount_consistency' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_payments payments
JOIN dw.dw_fact_sales sales ON sales.sales_key = payments.sales_key
WHERE ABS(payments.payment_amount - sales.net_amount) > 0.011;

SELECT 'fact_inventory_consistency' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_inventory inventory
JOIN dw.dw_fact_sales sales ON sales.sales_key = inventory.sales_key
WHERE inventory.quantity_sold <> sales.quantity
   OR inventory.stock_after_sale <> inventory.stock_before_sale - inventory.quantity_sold;
