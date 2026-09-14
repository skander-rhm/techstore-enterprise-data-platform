CREATE SCHEMA IF NOT EXISTS analytics;

SELECT 'analytics_views_present' AS check_name,
       CASE WHEN COUNT(*) = 6 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM information_schema.views
WHERE table_schema = 'analytics'
  AND table_name IN ('vw_sales_kpis', 'vw_monthly_sales', 'vw_product_performance', 'vw_customer_performance', 'vw_store_performance', 'vw_returns_analysis');

SELECT 'sales_kpi_non_negative' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM analytics.vw_sales_kpis
WHERE total_revenue < 0 OR net_revenue < 0 OR total_cost < 0 OR total_quantity_sold < 0
   OR number_of_sales < 0 OR number_of_returned_sales < 0 OR return_rate < 0;

SELECT 'sales_kpi_no_division_by_zero' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM analytics.vw_sales_kpis
WHERE gross_margin_pct IS NULL
   OR average_order_value IS NULL
   OR return_rate IS NULL;

SELECT 'sales_margin_reconciliation' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_sales
WHERE ABS(margin_amount - (net_amount - total_cost)) > 0.011;

SELECT 'monthly_sales_unique_grain' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM (
    SELECT calendar_year, calendar_month
    FROM analytics.vw_monthly_sales
    GROUP BY calendar_year, calendar_month
    HAVING COUNT(*) > 1
) duplicate_months;

SELECT 'monthly_sales_date_coherence' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM analytics.vw_monthly_sales
WHERE EXTRACT(YEAR FROM month_start)::INTEGER <> calendar_year
   OR EXTRACT(MONTH FROM month_start)::INTEGER <> calendar_month;

SELECT 'product_performance_unique_grain' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM (
    SELECT product_key
    FROM analytics.vw_product_performance
    GROUP BY product_key
    HAVING COUNT(*) > 1
) duplicate_products;

SELECT 'customer_performance_unique_grain' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM (
    SELECT customer_key
    FROM analytics.vw_customer_performance
    GROUP BY customer_key
    HAVING COUNT(*) > 1
) duplicate_customers;

SELECT 'store_performance_unique_grain' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM (
    SELECT store_key
    FROM analytics.vw_store_performance
    GROUP BY store_key
    HAVING COUNT(*) > 1
) duplicate_stores;

SELECT 'monthly_revenue_matches_sales' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM (
    SELECT monthly.calendar_year, monthly.calendar_month,
           monthly.net_revenue,
           SUM(sales.net_amount) AS expected_net_revenue
    FROM analytics.vw_monthly_sales monthly
    JOIN dw.dw_dim_date date
      ON date.calendar_year = monthly.calendar_year
     AND date.calendar_month = monthly.calendar_month
    JOIN dw.dw_fact_sales sales ON sales.sale_date_key = date.date_key
    GROUP BY monthly.calendar_year, monthly.calendar_month, monthly.net_revenue
) comparison
WHERE ABS(net_revenue - expected_net_revenue) > 0.011;

SELECT 'payment_reconciliation' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_payments payments
JOIN dw.dw_fact_sales sales ON sales.sales_key = payments.sales_key
WHERE ABS(payments.payment_amount - sales.net_amount) > 0.011;

SELECT 'inventory_reconciliation' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_value
FROM dw.dw_fact_inventory inventory
JOIN dw.dw_fact_sales sales ON sales.sales_key = inventory.sales_key
WHERE inventory.quantity_sold <> sales.quantity
   OR inventory.stock_after_sale <> inventory.stock_before_sale - inventory.quantity_sold;
