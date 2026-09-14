CREATE TABLE IF NOT EXISTS dw.dw_dim_supplier (
    supplier_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id VARCHAR(50) NOT NULL UNIQUE,
    supplier_name TEXT NOT NULL,
    supplier_country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dw_dim_store (
    store_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL UNIQUE,
    store_name TEXT NOT NULL,
    store_city TEXT NOT NULL,
    store_country TEXT NOT NULL,
    store_region TEXT NOT NULL,
    store_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dw_dim_customer (
    customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_full_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_gender TEXT NOT NULL,
    customer_city TEXT NOT NULL,
    customer_segment TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dw_dim_employee (
    employee_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    employee_full_name TEXT NOT NULL,
    employee_role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dw_dim_date (
    date_key INTEGER PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    calendar_year SMALLINT NOT NULL,
    calendar_quarter SMALLINT NOT NULL,
    calendar_month SMALLINT NOT NULL,
    calendar_day SMALLINT NOT NULL,
    weekday_name VARCHAR(15) NOT NULL,
    CONSTRAINT ck_dw_dim_date_key_format CHECK (date_key BETWEEN 19000101 AND 29991231),
    CONSTRAINT ck_dw_dim_date_parts CHECK (
        calendar_quarter BETWEEN 1 AND 4
        AND calendar_month BETWEEN 1 AND 12
        AND calendar_day BETWEEN 1 AND 31
    )
);

CREATE TABLE IF NOT EXISTS dw.dw_dim_product (
    product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_subcategory TEXT NOT NULL,
    product_brand TEXT NOT NULL,
    product_warranty_months INTEGER NOT NULL,
    supplier_key BIGINT NOT NULL REFERENCES dw.dw_dim_supplier(supplier_key),
    CONSTRAINT ck_dw_dim_product_warranty CHECK (product_warranty_months >= 0)
);

CREATE TABLE IF NOT EXISTS dw.dw_dim_warehouse (
    warehouse_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_id VARCHAR(50) NOT NULL UNIQUE,
    store_key BIGINT NOT NULL REFERENCES dw.dw_dim_store(store_key)
);
