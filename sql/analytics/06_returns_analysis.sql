-- Overall return rate.
SELECT
    COUNT(*) AS number_of_sales,
    COUNT(*) FILTER (WHERE is_returned) AS returned_sales,
    COUNT(*) FILTER (WHERE is_returned)::NUMERIC / NULLIF(COUNT(*), 0) AS return_rate,
    SUM(refunds.refund_amount) AS total_refunds
FROM dw.dw_fact_sales sales
LEFT JOIN dw.dw_fact_returns refunds ON refunds.sales_key = sales.sales_key;

-- Returns by product.
SELECT
    product.product_id,
    product.product_name,
    COUNT(returns.return_key) AS number_of_returns,
    SUM(returns.refund_amount) AS total_refunds,
    COUNT(returns.return_key)::NUMERIC / NULLIF(COUNT(sales.sales_key), 0) AS return_rate
FROM dw.dw_dim_product product
JOIN dw.dw_fact_sales sales ON sales.product_key = product.product_key
LEFT JOIN dw.dw_fact_returns returns ON returns.sales_key = sales.sales_key
GROUP BY product.product_id, product.product_name
HAVING COUNT(returns.return_key) > 0
ORDER BY number_of_returns DESC;

-- Returns by store.
SELECT
    store.store_id,
    store.store_name,
    COUNT(returns.return_key) AS number_of_returns,
    SUM(returns.refund_amount) AS total_refunds
FROM dw.dw_dim_store store
JOIN dw.dw_fact_sales sales ON sales.store_key = store.store_key
LEFT JOIN dw.dw_fact_returns returns ON returns.sales_key = sales.sales_key
GROUP BY store.store_id, store.store_name
HAVING COUNT(returns.return_key) > 0
ORDER BY number_of_returns DESC;

-- Returns by customer.
SELECT
    customer.customer_id,
    customer.customer_full_name,
    COUNT(returns.return_key) AS number_of_returns,
    SUM(returns.refund_amount) AS total_refunds
FROM dw.dw_dim_customer customer
JOIN dw.dw_fact_sales sales ON sales.customer_key = customer.customer_key
JOIN dw.dw_fact_returns returns ON returns.sales_key = sales.sales_key
GROUP BY customer.customer_id, customer.customer_full_name
ORDER BY number_of_returns DESC
LIMIT 10;

-- Returns by month.
SELECT
    date.calendar_year,
    date.calendar_month,
    COUNT(*) AS number_of_returns,
    SUM(returns.refund_amount) AS total_refunds
FROM dw.dw_fact_returns returns
JOIN dw.dw_dim_date date ON date.date_key = returns.return_date_key
GROUP BY date.calendar_year, date.calendar_month
ORDER BY date.calendar_year, date.calendar_month;

-- Return reasons.
SELECT
    return_reason,
    COUNT(*) AS number_of_returns,
    SUM(refund_amount) AS total_refunds,
    COUNT(*)::NUMERIC / NULLIF(SUM(COUNT(*)) OVER (), 0) AS reason_share
FROM dw.dw_fact_returns
GROUP BY return_reason
ORDER BY number_of_returns DESC;
