-- Top customers by net revenue.
SELECT *
FROM analytics.vw_customer_performance
WHERE number_of_orders > 0
ORDER BY net_revenue DESC
LIMIT 10;

-- Top customers by gross margin.
SELECT *
FROM analytics.vw_customer_performance
WHERE number_of_orders > 0
ORDER BY gross_margin DESC
LIMIT 10;

-- Customer order count, average order value and return frequency.
SELECT
    customer_key,
    customer_id,
    customer_full_name,
    number_of_orders,
    average_order_value,
    number_of_returns,
    number_of_returns::NUMERIC / NULLIF(number_of_orders, 0) AS return_rate,
    value_segment
FROM analytics.vw_customer_performance
WHERE number_of_orders > 0
ORDER BY number_of_orders DESC;

-- Customers with frequent returns.
SELECT *
FROM analytics.vw_customer_performance
WHERE number_of_returns > 0
ORDER BY number_of_returns DESC,
         number_of_returns::NUMERIC / NULLIF(number_of_orders, 0) DESC
LIMIT 10;

-- Simple revenue-based segmentation.
SELECT
    value_segment,
    COUNT(*) FILTER (WHERE number_of_orders > 0) AS active_customers,
    SUM(net_revenue) AS net_revenue,
    SUM(gross_margin) AS gross_margin,
    AVG(average_order_value) FILTER (WHERE number_of_orders > 0) AS average_order_value
FROM analytics.vw_customer_performance
GROUP BY value_segment
ORDER BY CASE value_segment WHEN 'High Value' THEN 1 WHEN 'Medium Value' THEN 2 ELSE 3 END;
