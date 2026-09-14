-- Overall payment reconciliation.
SELECT
    COUNT(*) AS number_of_payments,
    SUM(payment_amount) AS total_amount_paid,
    AVG(payment_amount) AS average_payment_amount,
    COUNT(*) FILTER (WHERE payment_amount < 0) AS negative_payment_count,
    SUM(payment_amount) - (SELECT SUM(net_amount) FROM dw.dw_fact_sales) AS payment_sales_difference
FROM dw.dw_fact_payments;

-- Payments by method and status.
SELECT
    payment_method,
    payment_status,
    COUNT(*) AS number_of_payments,
    SUM(payment_amount) AS total_amount_paid,
    AVG(payment_amount) AS average_payment_amount
FROM dw.dw_fact_payments
GROUP BY payment_method, payment_status
ORDER BY total_amount_paid DESC;

-- Payment and sale comparison by currency.
SELECT
    payments.currency,
    COUNT(*) AS number_of_payments,
    SUM(payments.payment_amount) AS total_amount_paid,
    SUM(sales.net_amount) AS related_net_revenue,
    SUM(payments.payment_amount) - SUM(sales.net_amount) AS difference
FROM dw.dw_fact_payments payments
JOIN dw.dw_fact_sales sales ON sales.sales_key = payments.sales_key
GROUP BY payments.currency
ORDER BY payments.currency;

-- Payment anomalies against the related sale.
SELECT
    payments.sale_id,
    payments.payment_amount,
    sales.net_amount,
    payments.payment_status,
    payments.payment_amount - sales.net_amount AS difference
FROM dw.dw_fact_payments payments
JOIN dw.dw_fact_sales sales ON sales.sales_key = payments.sales_key
WHERE ABS(payments.payment_amount - sales.net_amount) > 0.011
   OR payments.payment_status IS NULL;
