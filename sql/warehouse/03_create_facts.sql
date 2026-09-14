CREATE TABLE IF NOT EXISTS dw.dw_fact_sales (
    sales_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_id VARCHAR(50) NOT NULL UNIQUE,
    sale_date_key INTEGER NOT NULL REFERENCES dw.dw_dim_date(date_key),
    delivery_date_key INTEGER REFERENCES dw.dw_dim_date(date_key),
    customer_key BIGINT NOT NULL REFERENCES dw.dw_dim_customer(customer_key),
    product_key BIGINT NOT NULL REFERENCES dw.dw_dim_product(product_key),
    employee_key BIGINT NOT NULL REFERENCES dw.dw_dim_employee(employee_key),
    store_key BIGINT NOT NULL REFERENCES dw.dw_dim_store(store_key),
    warehouse_key BIGINT NOT NULL REFERENCES dw.dw_dim_warehouse(warehouse_key),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(18, 2) NOT NULL,
    unit_cost NUMERIC(18, 2) NOT NULL,
    discount_pct NUMERIC(9, 6) NOT NULL,
    gross_amount NUMERIC(18, 2) NOT NULL,
    discount_amount NUMERIC(18, 2) NOT NULL,
    net_amount NUMERIC(18, 2) NOT NULL,
    total_cost NUMERIC(18, 2) NOT NULL,
    margin_amount NUMERIC(18, 2) NOT NULL,
    margin_pct NUMERIC(9, 6) NOT NULL,
    sales_channel TEXT NOT NULL,
    delivery_method TEXT NOT NULL,
    shipping_cost NUMERIC(18, 2) NOT NULL,
    shipping_cost_imputed BOOLEAN NOT NULL,
    order_status TEXT NOT NULL,
    is_returned BOOLEAN NOT NULL,
    customer_satisfaction_score NUMERIC(3, 1),
    customer_age SMALLINT,
    customer_age_imputed BOOLEAN NOT NULL,
    CONSTRAINT ck_dw_fact_sales_quantity CHECK (quantity > 0),
    CONSTRAINT ck_dw_fact_sales_amounts CHECK (
        unit_price >= 0 AND unit_cost >= 0 AND shipping_cost >= 0
    ),
    CONSTRAINT ck_dw_fact_sales_discount CHECK (discount_pct BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS dw.dw_fact_returns (
    return_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_id VARCHAR(50) NOT NULL UNIQUE,
    sales_key BIGINT NOT NULL REFERENCES dw.dw_fact_sales(sales_key),
    return_date_key INTEGER NOT NULL REFERENCES dw.dw_dim_date(date_key),
    return_reason TEXT NOT NULL,
    refund_amount NUMERIC(18, 2) NOT NULL,
    CONSTRAINT ck_dw_fact_returns_refund CHECK (refund_amount >= 0)
);

CREATE TABLE IF NOT EXISTS dw.dw_fact_payments (
    payment_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_id VARCHAR(50) NOT NULL UNIQUE,
    sales_key BIGINT NOT NULL REFERENCES dw.dw_fact_sales(sales_key),
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    payment_amount NUMERIC(18, 2) NOT NULL,
    CONSTRAINT ck_dw_fact_payments_amount CHECK (payment_amount >= 0)
);

CREATE TABLE IF NOT EXISTS dw.dw_fact_inventory (
    inventory_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_id VARCHAR(50) NOT NULL UNIQUE,
    sales_key BIGINT NOT NULL REFERENCES dw.dw_fact_sales(sales_key),
    product_key BIGINT NOT NULL REFERENCES dw.dw_dim_product(product_key),
    warehouse_key BIGINT NOT NULL REFERENCES dw.dw_dim_warehouse(warehouse_key),
    quantity_sold INTEGER NOT NULL,
    stock_before_sale INTEGER NOT NULL,
    stock_after_sale INTEGER NOT NULL,
    CONSTRAINT ck_dw_fact_inventory_quantity CHECK (quantity_sold > 0),
    CONSTRAINT ck_dw_fact_inventory_stock CHECK (
        stock_before_sale >= 0 AND stock_after_sale >= 0
        AND stock_after_sale = stock_before_sale - quantity_sold
    )
);
