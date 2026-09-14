-- Executive KPI view.
SELECT * FROM analytics.vw_sales_kpis;

-- Revenue and margin by sales channel.
SELECT
    sales_channel,
    COUNT(*) AS number_of_sales,
    SUM(net_amount) AS net_revenue,
    SUM(margin_amount) AS gross_margin,
    SUM(margin_amount) / NULLIF(SUM(net_amount), 0) AS gross_margin_pct,
    SUM(quantity) AS total_quantity_sold
FROM dw.dw_fact_sales
GROUP BY sales_channel
ORDER BY net_revenue DESC;

-- Revenue and margin by order status.
SELECT
    order_status,
    COUNT(*) AS number_of_sales,
    SUM(net_amount) AS net_revenue,
    SUM(margin_amount) AS gross_margin,
    SUM(quantity) AS total_quantity_sold
FROM dw.dw_fact_sales
GROUP BY order_status
ORDER BY net_revenue DESC;

-- Revenue and margin by delivery method.
SELECT
    delivery_method,
    COUNT(*) AS number_of_sales,
    SUM(net_amount) AS net_revenue,
    SUM(shipping_cost) AS total_shipping_cost,
    SUM(margin_amount) AS gross_margin
FROM dw.dw_fact_sales
GROUP BY delivery_method
ORDER BY net_revenue DESC;
