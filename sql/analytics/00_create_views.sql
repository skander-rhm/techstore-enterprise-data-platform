CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.vw_sales_kpis AS
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

CREATE OR REPLACE VIEW analytics.vw_monthly_sales AS
WITH monthly AS (
    SELECT
        date.calendar_year,
        date.calendar_month,
        MIN(date.calendar_date) AS month_start,
        SUM(sales.gross_amount) AS total_revenue,
        SUM(sales.net_amount) AS net_revenue,
        SUM(sales.total_cost) AS total_cost,
        SUM(sales.margin_amount) AS gross_margin,
        SUM(sales.quantity) AS total_quantity_sold,
        COUNT(*) AS number_of_sales
    FROM dw.dw_fact_sales sales
    JOIN dw.dw_dim_date date ON date.date_key = sales.sale_date_key
    GROUP BY date.calendar_year, date.calendar_month
)
SELECT
    calendar_year,
    calendar_month,
    month_start,
    total_revenue,
    net_revenue,
    total_cost,
    gross_margin,
    total_quantity_sold,
    number_of_sales,
    gross_margin / NULLIF(net_revenue, 0) AS gross_margin_pct,
    LAG(net_revenue) OVER (ORDER BY calendar_year, calendar_month) AS previous_month_net_revenue,
    net_revenue - LAG(net_revenue) OVER (ORDER BY calendar_year, calendar_month) AS month_over_month_change,
    (net_revenue / NULLIF(LAG(net_revenue) OVER (ORDER BY calendar_year, calendar_month), 0)) - 1 AS month_over_month_growth
FROM monthly;

CREATE OR REPLACE VIEW analytics.vw_product_performance AS
SELECT
    product.product_key,
    product.product_id,
    product.product_name,
    product.product_category,
    product.product_brand,
    COUNT(sales.sales_key) AS number_of_sales,
    SUM(sales.quantity) AS total_quantity_sold,
    SUM(sales.net_amount) AS net_revenue,
    SUM(sales.margin_amount) AS gross_margin,
    SUM(sales.margin_amount) / NULLIF(SUM(sales.net_amount), 0) AS gross_margin_pct,
    COUNT(*) FILTER (WHERE sales.is_returned) AS number_of_returns,
    COUNT(*) FILTER (WHERE sales.is_returned)::NUMERIC / NULLIF(COUNT(*), 0) AS return_rate
FROM dw.dw_dim_product product
LEFT JOIN dw.dw_fact_sales sales ON sales.product_key = product.product_key
GROUP BY product.product_key, product.product_id, product.product_name, product.product_category, product.product_brand;

CREATE OR REPLACE VIEW analytics.vw_customer_performance AS
SELECT
    customer.customer_key,
    customer.customer_id,
    customer.customer_full_name,
    customer.customer_segment,
    COUNT(sales.sales_key) AS number_of_orders,
    SUM(sales.net_amount) AS net_revenue,
    SUM(sales.margin_amount) AS gross_margin,
    SUM(sales.quantity) AS total_quantity_sold,
    SUM(sales.net_amount) / NULLIF(COUNT(sales.sales_key), 0) AS average_order_value,
    COUNT(*) FILTER (WHERE sales.is_returned) AS number_of_returns,
    CASE
        WHEN SUM(sales.net_amount) >= 10000 THEN 'High Value'
        WHEN SUM(sales.net_amount) >= 3000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS value_segment
FROM dw.dw_dim_customer customer
LEFT JOIN dw.dw_fact_sales sales ON sales.customer_key = customer.customer_key
GROUP BY customer.customer_key, customer.customer_id, customer.customer_full_name, customer.customer_segment;

CREATE OR REPLACE VIEW analytics.vw_store_performance AS
SELECT
    store.store_key,
    store.store_id,
    store.store_name,
    store.store_city,
    store.store_region,
    COUNT(sales.sales_key) AS number_of_sales,
    SUM(sales.net_amount) AS net_revenue,
    SUM(sales.margin_amount) AS gross_margin,
    SUM(sales.quantity) AS total_quantity_sold,
    SUM(sales.net_amount) / NULLIF(COUNT(sales.sales_key), 0) AS average_order_value,
    RANK() OVER (ORDER BY SUM(sales.net_amount) DESC) AS revenue_rank
FROM dw.dw_dim_store store
LEFT JOIN dw.dw_fact_sales sales ON sales.store_key = store.store_key
GROUP BY store.store_key, store.store_id, store.store_name, store.store_city, store.store_region;

CREATE OR REPLACE VIEW analytics.vw_returns_analysis AS
SELECT
    date.calendar_year,
    date.calendar_month,
    date.calendar_date AS return_date,
    product.product_key,
    product.product_id,
    product.product_name,
    store.store_key,
    store.store_id,
    customer.customer_key,
    customer.customer_id,
    returns.return_reason,
    returns.refund_amount,
    sales.net_amount AS sale_net_amount
FROM dw.dw_fact_returns returns
JOIN dw.dw_fact_sales sales ON sales.sales_key = returns.sales_key
JOIN dw.dw_dim_date date ON date.date_key = returns.return_date_key
JOIN dw.dw_dim_product product ON product.product_key = sales.product_key
JOIN dw.dw_dim_store store ON store.store_key = sales.store_key
JOIN dw.dw_dim_customer customer ON customer.customer_key = sales.customer_key;
