-- Store performance and ranking.
SELECT *
FROM analytics.vw_store_performance
ORDER BY revenue_rank;

-- Employee performance.
SELECT
    employee.employee_key,
    employee.employee_id,
    employee.employee_full_name,
    employee.employee_role,
    COUNT(sales.sales_key) AS number_of_sales,
    SUM(sales.net_amount) AS net_revenue,
    SUM(sales.margin_amount) AS gross_margin,
    SUM(sales.quantity) AS total_quantity_sold,
    SUM(sales.net_amount) / NULLIF(COUNT(sales.sales_key), 0) AS average_sale_value,
    RANK() OVER (ORDER BY SUM(sales.net_amount) DESC) AS revenue_rank
FROM dw.dw_dim_employee employee
LEFT JOIN dw.dw_fact_sales sales ON sales.employee_key = employee.employee_key
GROUP BY employee.employee_key, employee.employee_id, employee.employee_full_name, employee.employee_role
ORDER BY revenue_rank;

-- Store and employee comparison at their respective grains.
SELECT
    'store' AS entity_type,
    store_id AS entity_id,
    store_name AS entity_name,
    number_of_sales,
    net_revenue,
    gross_margin,
    total_quantity_sold,
    revenue_rank
FROM analytics.vw_store_performance
UNION ALL
SELECT
    'employee',
    employee.employee_id,
    employee.employee_full_name,
    COUNT(sales.sales_key),
    SUM(sales.net_amount),
    SUM(sales.margin_amount),
    SUM(sales.quantity),
    RANK() OVER (ORDER BY SUM(sales.net_amount) DESC)
FROM dw.dw_dim_employee employee
LEFT JOIN dw.dw_fact_sales sales ON sales.employee_key = employee.employee_key
GROUP BY employee.employee_id, employee.employee_full_name
ORDER BY entity_type, revenue_rank;
