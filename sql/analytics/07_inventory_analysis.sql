-- Inventory snapshot/movement grain: one row per sale, product and warehouse.
SELECT
    product.product_id,
    product.product_name,
    warehouse.warehouse_id,
    COUNT(*) AS inventory_events,
    AVG(inventory.stock_before_sale) AS average_stock_before_sale,
    MIN(inventory.stock_after_sale) AS minimum_stock_after_sale,
    MAX(inventory.stock_after_sale) AS maximum_stock_after_sale,
    SUM(inventory.quantity_sold) AS total_quantity_sold
FROM dw.dw_fact_inventory inventory
JOIN dw.dw_dim_product product ON product.product_key = inventory.product_key
JOIN dw.dw_dim_warehouse warehouse ON warehouse.warehouse_key = inventory.warehouse_key
GROUP BY product.product_id, product.product_name, warehouse.warehouse_id
ORDER BY average_stock_before_sale;

-- Products at risk of stockout at the observed event grain.
SELECT
    product.product_id,
    product.product_name,
    MIN(inventory.stock_after_sale) AS minimum_stock_after_sale,
    AVG(inventory.stock_after_sale) AS average_stock_after_sale,
    SUM(inventory.quantity_sold) AS total_quantity_sold
FROM dw.dw_fact_inventory inventory
JOIN dw.dw_dim_product product ON product.product_key = inventory.product_key
GROUP BY product.product_id, product.product_name
HAVING MIN(inventory.stock_after_sale) <= 10
ORDER BY minimum_stock_after_sale, total_quantity_sold DESC;

-- Warehouses with low observed stock.
SELECT
    warehouse.warehouse_id,
    store.store_name,
    AVG(inventory.stock_after_sale) AS average_stock_after_sale,
    MIN(inventory.stock_after_sale) AS minimum_stock_after_sale,
    MAX(inventory.stock_after_sale) AS maximum_stock_after_sale,
    SUM(inventory.quantity_sold) AS total_quantity_sold
FROM dw.dw_fact_inventory inventory
JOIN dw.dw_dim_warehouse warehouse ON warehouse.warehouse_key = inventory.warehouse_key
JOIN dw.dw_dim_store store ON store.store_key = warehouse.store_key
GROUP BY warehouse.warehouse_id, store.store_name
ORDER BY average_stock_after_sale;

-- Stock evolution by month using the sale date associated with each inventory event.
SELECT
    date.calendar_year,
    date.calendar_month,
    AVG(inventory.stock_before_sale) AS average_stock_before_sale,
    AVG(inventory.stock_after_sale) AS average_stock_after_sale,
    SUM(inventory.quantity_sold) AS total_quantity_sold
FROM dw.dw_fact_inventory inventory
JOIN dw.dw_fact_sales sales ON sales.sales_key = inventory.sales_key
JOIN dw.dw_dim_date date ON date.date_key = sales.sale_date_key
GROUP BY date.calendar_year, date.calendar_month
ORDER BY date.calendar_year, date.calendar_month;
