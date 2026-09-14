"""Load validated Gold CSV files into the PostgreSQL data warehouse."""

from __future__ import annotations

import csv
import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

try:
    import psycopg
    from psycopg import sql
except ImportError:  # pragma: no cover - exercised when the optional runtime is absent
    psycopg = None
    sql = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
SQL_DIR = PROJECT_ROOT / "sql" / "warehouse"
AUDIT_FILE = GOLD_DIR / "warehouse_load_audit.json"
LOGGER = logging.getLogger("techstore.warehouse_loader")

DDL_FILES = [
    "01_create_schema.sql",
    "02_create_dimensions.sql",
    "03_create_facts.sql",
    "04_create_indexes.sql",
]

DIMENSION_LOADS = [
    ("dim_date", "dw_dim_date", ["date_key", "date", "year", "quarter", "month", "day", "weekday"],
     ["date_key", "calendar_date", "calendar_year", "calendar_quarter", "calendar_month", "calendar_day", "weekday_name"], None),
    ("dim_supplier", "dw_dim_supplier", ["supplier_id", "supplier_name", "supplier_country"],
     ["supplier_id", "supplier_name", "supplier_country"], None),
    ("dim_store", "dw_dim_store", ["store_id", "store_name", "store_city", "store_country", "store_region", "store_type"],
     ["store_id", "store_name", "store_city", "store_country", "store_region", "store_type"], None),
    ("dim_warehouse", "dw_dim_warehouse", ["warehouse_id", "store_id"],
     ["warehouse_id", "store_key"], "store_key"),
    ("dim_customer", "dw_dim_customer", ["customer_id", "customer_full_name", "customer_email", "customer_gender", "customer_city", "customer_segment"],
     ["customer_id", "customer_full_name", "customer_email", "customer_gender", "customer_city", "customer_segment"], None),
    ("dim_product", "dw_dim_product", ["product_id", "product_name", "product_category", "product_subcategory", "product_brand", "product_warranty_months", "supplier_id"],
     ["product_id", "product_name", "product_category", "product_subcategory", "product_brand", "product_warranty_months", "supplier_key"], "supplier_key"),
    ("dim_employee", "dw_dim_employee", ["employee_id", "employee_full_name", "employee_role"],
     ["employee_id", "employee_full_name", "employee_role"], None),
]

FACT_LOADS = {
    "fact_sales": ("dw_fact_sales", [
        "sale_id", "sale_date_key", "delivery_date_key", "customer_key", "product_key", "employee_key", "store_key", "warehouse_key",
        "quantity", "unit_price", "unit_cost", "discount_pct", "gross_amount", "discount_amount", "net_amount", "total_cost",
        "margin_amount", "margin_pct", "sales_channel", "delivery_method", "shipping_cost", "shipping_cost_imputed", "order_status",
        "is_returned", "customer_satisfaction_score", "customer_age", "customer_age_imputed",
    ]),
    "fact_returns": ("dw_fact_returns", ["sale_id", "sales_key", "return_date_key", "return_reason", "refund_amount"]),
    "fact_payments": ("dw_fact_payments", ["sale_id", "sales_key", "payment_method", "payment_status", "currency", "payment_amount"]),
    "fact_inventory": ("dw_fact_inventory", ["sale_id", "sales_key", "product_key", "warehouse_key", "quantity_sold", "stock_before_sale", "stock_after_sale"]),
}


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def write_audit(audit: dict[str, Any]) -> None:
    AUDIT_FILE.write_text(json.dumps(audit, indent=2, ensure_ascii=True), encoding="utf-8")


def connection_kwargs() -> dict[str, Any]:
    return {
        "host": os.getenv("TECHSTORE_PGHOST", os.getenv("PGHOST", "localhost")),
        "port": int(os.getenv("TECHSTORE_PGPORT", os.getenv("PGPORT", "5432"))),
        "dbname": os.getenv("TECHSTORE_PGNAME", os.getenv("PGDATABASE", "postgres")),
        "user": os.getenv("TECHSTORE_PGUSER", os.getenv("PGUSER", "postgres")),
        "password": os.getenv("TECHSTORE_PGPASSWORD", os.getenv("PGPASSWORD", "")),
    }


def run_sql_files(cursor: Any) -> None:
    for filename in DDL_FILES:
        LOGGER.info("Executing %s", filename)
        cursor.execute((SQL_DIR / filename).read_text(encoding="utf-8"))


def truncate_dw(cursor: Any) -> None:
    tables = [
        "dw.dw_fact_inventory", "dw.dw_fact_payments", "dw.dw_fact_returns", "dw.dw_fact_sales",
        "dw.dw_dim_product", "dw.dw_dim_warehouse", "dw.dw_dim_employee", "dw.dw_dim_customer",
        "dw.dw_dim_store", "dw.dw_dim_supplier", "dw.dw_dim_date",
    ]
    cursor.execute("TRUNCATE TABLE " + ", ".join(tables) + " RESTART IDENTITY CASCADE")


def write_csv_file(source: Path, output_columns: list[str], transform: Callable[[dict[str, str]], list[Any]] | None) -> Path:
    descriptor, output_name = tempfile.mkstemp(prefix="techstore_dw_", suffix=".csv")
    os.close(descriptor)
    output = Path(output_name)
    try:
        with source.open("r", encoding="utf-8", newline="") as input_file, output.open("w", encoding="utf-8", newline="") as output_file:
            reader = csv.DictReader(input_file)
            writer = csv.writer(output_file, lineterminator="\n")
            for row in reader:
                values = transform(row) if transform else [row[column] or None for column in output_columns]
                writer.writerow(values)
        return output
    except Exception:
        output.unlink(missing_ok=True)
        raise


def copy_csv(cursor: Any, table: str, columns: list[str], csv_file: Path) -> int:
    statement = sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT CSV, NULL '')").format(
        sql.Identifier("dw", table),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )
    with csv_file.open("rb") as input_file, cursor.copy(statement) as copy:
        while chunk := input_file.read(1024 * 1024):
            copy.write(chunk)
    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}" ).format(sql.Identifier("dw", table)))
    return cursor.fetchone()[0]


def fetch_key_map(cursor: Any, table: str, business_column: str, surrogate_column: str) -> dict[str, int]:
    cursor.execute(sql.SQL("SELECT {}, {} FROM {}" ).format(
        sql.Identifier(business_column), sql.Identifier(surrogate_column), sql.Identifier("dw", table)
    ))
    return {str(business_key): surrogate_key for business_key, surrogate_key in cursor.fetchall()}


def load_dimensions(cursor: Any) -> dict[str, dict[str, int]]:
    maps: dict[str, dict[str, int]] = {}
    for source_name, target_name, source_columns, target_columns, map_name in DIMENSION_LOADS:
        source = GOLD_DIR / f"{source_name}.csv"
        transform: Callable[[dict[str, str]], list[Any]] | None = None
        if map_name == "store_key":
            store_map = maps["store_id"]
            transform = lambda row, store_map=store_map: [row["warehouse_id"], store_map[row["store_id"]]]
        elif map_name == "supplier_key":
            supplier_map = maps["supplier_id"]
            transform = lambda row, supplier_map=supplier_map: [row[column] for column in source_columns[:-1]] + [supplier_map[row["supplier_id"]]]
        csv_file = write_csv_file(source, source_columns, transform)
        try:
            count = copy_csv(cursor, target_name, target_columns, csv_file)
        finally:
            csv_file.unlink(missing_ok=True)
        LOGGER.info("Loaded %s: %d rows", target_name, count)
        if target_name == "dw_dim_date":
            continue
        business_key = source_columns[0]
        surrogate_key = target_name.removeprefix("dw_dim_").removesuffix("s") + "_key"
        maps[business_key] = fetch_key_map(cursor, target_name, business_key, surrogate_key)
    return maps


def load_facts(cursor: Any, maps: dict[str, dict[str, int]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    sales_map: dict[str, int] | None = None
    for source_name, (target_name, target_columns) in FACT_LOADS.items():
        source = GOLD_DIR / f"{source_name}.csv"

        def transform(row: dict[str, str], source_name: str = source_name) -> list[Any]:
            value = lambda key: row[key] or None
            if source_name == "fact_sales":
                return [value("sale_id"), value("sale_date_key"), value("delivery_date_key"), maps["customer_id"][row["customer_id"]], maps["product_id"][row["product_id"]], maps["employee_id"][row["employee_id"]], maps["store_id"][row["store_id"]], maps["warehouse_id"][row["warehouse_id"]]] + [value(column) for column in target_columns[8:]]
            if source_name == "fact_returns":
                return [value("sale_id"), sales_map[row["sale_id"]], value("return_date_key"), value("return_reason"), value("refund_amount")]
            if source_name == "fact_payments":
                return [value("sale_id"), sales_map[row["sale_id"]], value("payment_method"), value("payment_status"), value("currency"), value("payment_amount")]
            return [value("sale_id"), sales_map[row["sale_id"]], maps["product_id"][row["product_id"]], maps["warehouse_id"][row["warehouse_id"]], value("quantity_sold"), value("stock_before_sale"), value("stock_after_sale")]

        csv_file = write_csv_file(source, target_columns, transform)
        try:
            counts[target_name] = copy_csv(cursor, target_name, target_columns, csv_file)
        finally:
            csv_file.unlink(missing_ok=True)
        LOGGER.info("Loaded %s: %d rows", target_name, counts[target_name])
        if source_name == "fact_sales":
            sales_map = fetch_key_map(cursor, target_name, "sale_id", "sales_key")
    return counts


def run_quality_checks(cursor: Any) -> list[dict[str, Any]]:
    results = []
    for statement in (SQL_DIR / "05_quality_checks.sql").read_text(encoding="utf-8").split(";\n"):
        statement = statement.strip()
        if not statement:
            continue
        cursor.execute(statement)
        check_name, status, observed_value = cursor.fetchone()
        results.append({"check": check_name, "status": status, "observed_value": observed_value})
    return results


def count_csv_rows(source: Path) -> int:
    with source.open("r", encoding="utf-8", newline="") as input_file:
        return max(sum(1 for _ in input_file) - 1, 0)


def load() -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    audit: dict[str, Any] = {"started_at_utc": started.isoformat(), "status": "BLOCKED", "tables": {}, "quality_checks": []}
    if psycopg is None:
        audit["error"] = "Python package 'psycopg' is not installed. Install requirements.txt before loading."
        write_audit(audit)
        return audit
    try:
        with psycopg.connect(**connection_kwargs()) as connection:
            with connection.cursor() as cursor:
                run_sql_files(cursor)
                truncate_dw(cursor)
                dimension_maps = load_dimensions(cursor)
                load_facts(cursor, dimension_maps)
                source_tables = [(source_name, target_name) for source_name, target_name, *_ in DIMENSION_LOADS]
                source_tables.extend((source_name, target_name) for source_name, (target_name, _) in FACT_LOADS.items())
                for source_name, target_name in source_tables:
                    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}" ).format(sql.Identifier("dw", target_name)))
                    audit["tables"][target_name] = {
                        "source_rows": count_csv_rows(GOLD_DIR / f"{source_name}.csv"),
                        "destination_rows": cursor.fetchone()[0],
                    }
                audit["quality_checks"] = run_quality_checks(cursor)
                if any(check["status"] != "PASS" for check in audit["quality_checks"]):
                    raise RuntimeError("One or more warehouse quality checks failed")
        audit["status"] = "PASS"
    except Exception as error:
        LOGGER.exception("Warehouse load failed")
        audit["status"] = "FAIL"
        audit["error"] = str(error)
    audit["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_audit(audit)
    return audit


def main() -> None:
    configure_logging()
    audit = load()
    LOGGER.info("Warehouse load status: %s", audit["status"])
    if audit["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
