CREATE INDEX IF NOT EXISTS ix_dw_dim_product_supplier_key
    ON dw.dw_dim_product (supplier_key);

CREATE INDEX IF NOT EXISTS ix_dw_dim_warehouse_store_key
    ON dw.dw_dim_warehouse (store_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_sale_date_key
    ON dw.dw_fact_sales (sale_date_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_delivery_date_key
    ON dw.dw_fact_sales (delivery_date_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_customer_key
    ON dw.dw_fact_sales (customer_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_product_key
    ON dw.dw_fact_sales (product_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_employee_key
    ON dw.dw_fact_sales (employee_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_store_key
    ON dw.dw_fact_sales (store_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_sales_warehouse_key
    ON dw.dw_fact_sales (warehouse_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_returns_return_date_key
    ON dw.dw_fact_returns (return_date_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_returns_sales_key
    ON dw.dw_fact_returns (sales_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_payments_sales_key
    ON dw.dw_fact_payments (sales_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_inventory_sales_key
    ON dw.dw_fact_inventory (sales_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_inventory_product_key
    ON dw.dw_fact_inventory (product_key);

CREATE INDEX IF NOT EXISTS ix_dw_fact_inventory_warehouse_key
    ON dw.dw_fact_inventory (warehouse_key);
