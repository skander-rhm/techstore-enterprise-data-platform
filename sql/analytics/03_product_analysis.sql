-- Top 10 products by net revenue.
SELECT *
FROM analytics.vw_product_performance
ORDER BY net_revenue DESC NULLS LAST
LIMIT 10;

-- Top 10 products by gross margin.
SELECT *
FROM analytics.vw_product_performance
ORDER BY gross_margin DESC NULLS LAST
LIMIT 10;

-- Top 10 products by quantity sold.
SELECT *
FROM analytics.vw_product_performance
ORDER BY total_quantity_sold DESC NULLS LAST
LIMIT 10;

-- Products with positive sales and gross margin below 10%.
SELECT *
FROM analytics.vw_product_performance
WHERE number_of_sales > 0
  AND gross_margin_pct < 0.10
ORDER BY gross_margin_pct, net_revenue DESC;

-- Products with the highest return counts.
SELECT *
FROM analytics.vw_product_performance
WHERE number_of_returns > 0
ORDER BY number_of_returns DESC,
         number_of_returns::NUMERIC / NULLIF(number_of_sales, 0) DESC
LIMIT 10;

-- Performance by category.
SELECT
    product_category,
    COUNT(DISTINCT product_key) AS number_of_products,
    SUM(number_of_sales) AS number_of_sales,
    SUM(total_quantity_sold) AS total_quantity_sold,
    SUM(net_revenue) AS net_revenue,
    SUM(gross_margin) AS gross_margin,
    SUM(gross_margin) / NULLIF(SUM(net_revenue), 0) AS gross_margin_pct
FROM analytics.vw_product_performance
GROUP BY product_category
ORDER BY net_revenue DESC;

-- Performance by brand.
SELECT
    product_brand,
    COUNT(DISTINCT product_key) AS number_of_products,
    SUM(number_of_sales) AS number_of_sales,
    SUM(total_quantity_sold) AS total_quantity_sold,
    SUM(net_revenue) AS net_revenue,
    SUM(gross_margin) AS gross_margin,
    SUM(gross_margin) / NULLIF(SUM(net_revenue), 0) AS gross_margin_pct
FROM analytics.vw_product_performance
GROUP BY product_brand
ORDER BY net_revenue DESC;
