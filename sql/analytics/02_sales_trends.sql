-- Grain: one row per calendar year.
SELECT
    date.calendar_year,
    SUM(sales.gross_amount) AS total_revenue,
    SUM(sales.net_amount) AS net_revenue,
    SUM(sales.margin_amount) AS gross_margin,
    SUM(sales.quantity) AS total_quantity_sold,
    COUNT(*) AS number_of_sales,
    SUM(sales.margin_amount) / NULLIF(SUM(sales.net_amount), 0) AS gross_margin_pct
FROM dw.dw_fact_sales sales
JOIN dw.dw_dim_date date ON date.date_key = sales.sale_date_key
GROUP BY date.calendar_year
ORDER BY date.calendar_year;

-- Grain: one row per year and quarter.
SELECT
    date.calendar_year,
    date.calendar_quarter,
    SUM(sales.net_amount) AS net_revenue,
    SUM(sales.margin_amount) AS gross_margin,
    SUM(sales.quantity) AS total_quantity_sold,
    COUNT(*) AS number_of_sales
FROM dw.dw_fact_sales sales
JOIN dw.dw_dim_date date ON date.date_key = sales.sale_date_key
GROUP BY date.calendar_year, date.calendar_quarter
ORDER BY date.calendar_year, date.calendar_quarter;

-- Grain: one row per month, including month-over-month evolution.
SELECT *
FROM analytics.vw_monthly_sales
ORDER BY calendar_year, calendar_month;

-- Grain: one row per year, with year-over-year growth.
WITH yearly AS (
    SELECT
        date.calendar_year,
        SUM(sales.net_amount) AS net_revenue,
        SUM(sales.margin_amount) AS gross_margin,
        SUM(sales.quantity) AS total_quantity_sold
    FROM dw.dw_fact_sales sales
    JOIN dw.dw_dim_date date ON date.date_key = sales.sale_date_key
    GROUP BY date.calendar_year
)
SELECT
    calendar_year,
    net_revenue,
    gross_margin,
    total_quantity_sold,
    LAG(net_revenue) OVER (ORDER BY calendar_year) AS previous_year_net_revenue,
    net_revenue - LAG(net_revenue) OVER (ORDER BY calendar_year) AS yoy_revenue_change,
    (net_revenue / NULLIF(LAG(net_revenue) OVER (ORDER BY calendar_year), 0)) - 1 AS yoy_revenue_growth
FROM yearly
ORDER BY calendar_year;
