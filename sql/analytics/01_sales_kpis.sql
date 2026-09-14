-- Grain: one row for the whole sales fact.
SELECT
    COUNT(*) AS number_of_sales,
    SUM(gross_amount) AS total_revenue,
    SUM(net_amount) AS net_revenue,
    SUM(total_cost) AS total_cost,
    SUM(margin_amount) AS gross_margin,
    SUM(margin_amount) / NULLIF(SUM(net_amount), 0) AS gross_margin_pct,
    SUM(quantity) AS total_quantity_sold,
    SUM(net_amount) / NULLIF(COUNT(*), 0) AS average_order_value,
    AVG(unit_price) AS average_unit_price,
    AVG(discount_pct) AS average_discount_pct,
    COUNT(DISTINCT customer_key) AS number_of_customers,
    COUNT(DISTINCT product_key) AS number_of_products_sold,
    COUNT(*) FILTER (WHERE is_returned) AS number_of_returned_sales,
    COUNT(*) FILTER (WHERE is_returned)::NUMERIC / NULLIF(COUNT(*), 0) AS return_rate
FROM dw.dw_fact_sales;

-- Reusable view equivalent for BI consumers.
SELECT * FROM analytics.vw_sales_kpis;
