"""Split the validated TechStore Silver dataset into Gold business tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_FILE = PROJECT_ROOT / "data" / "silver" / "techstore_cleaned.csv"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
REPORT_FILE = PROJECT_ROOT / "docs" / "reports" / "transformation_report.md"


def distinct(dataframe: pd.DataFrame, columns: list[str], key: str) -> pd.DataFrame:
    """Create a deterministic dimension and fail if an ID maps to conflicting attributes."""
    conflicts = dataframe.groupby(key, dropna=False)[columns].nunique(dropna=False).gt(1).any(axis=1)
    if conflicts.any():
        raise ValueError(f"Attributs contradictoires pour {int(conflicts.sum())} valeur(s) de {key}.")
    return dataframe[columns].drop_duplicates(subset=[key]).sort_values(key).reset_index(drop=True)


def date_dimension(dataframe: pd.DataFrame) -> pd.DataFrame:
    dates = pd.concat(
        [dataframe["sale_date"], dataframe["delivery_date"], dataframe["return_date"]], ignore_index=True
    ).dropna()
    dates = pd.to_datetime(dates).drop_duplicates().sort_values().reset_index(drop=True)
    dim_date = pd.DataFrame({"date": dates})
    dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["weekday"] = dim_date["date"].dt.day_name()
    dim_date["date"] = dim_date["date"].dt.strftime("%Y-%m-%d")
    return dim_date[["date_key", "date", "year", "quarter", "month", "day", "weekday"]]


def add_date_keys(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    for source_column, key_column in (
        ("sale_date", "sale_date_key"),
        ("delivery_date", "delivery_date_key"),
        ("return_date", "return_date_key"),
    ):
        result[key_column] = pd.to_datetime(result[source_column]).dt.strftime("%Y%m%d").astype("Int64")
    return result


def fk_missing(child: pd.Series, parent: pd.Series) -> int:
    return int((~child.dropna().isin(parent)).sum())


def quality_checks(tables: dict[str, pd.DataFrame], silver_rows: int) -> dict[str, Any]:
    primary_keys = {
        "dim_customer": "customer_id", "dim_product": "product_id", "dim_supplier": "supplier_id",
        "dim_employee": "employee_id", "dim_store": "store_id", "dim_warehouse": "warehouse_id",
        "dim_date": "date_key", "fact_sales": "sale_id", "fact_returns": "sale_id",
        "fact_payments": "sale_id", "fact_inventory": "sale_id",
    }
    primary_key_issues = {
        table: int(frame[key].isna().sum() + frame[key].duplicated().sum())
        for table, (frame, key) in ((name, (tables[name], column)) for name, column in primary_keys.items())
    }
    fk_pairs = {
        "dim_product.supplier_id -> dim_supplier": (tables["dim_product"].supplier_id, tables["dim_supplier"].supplier_id),
        "dim_warehouse.store_id -> dim_store": (tables["dim_warehouse"].store_id, tables["dim_store"].store_id),
        "fact_sales.customer_id -> dim_customer": (tables["fact_sales"].customer_id, tables["dim_customer"].customer_id),
        "fact_sales.product_id -> dim_product": (tables["fact_sales"].product_id, tables["dim_product"].product_id),
        "fact_sales.employee_id -> dim_employee": (tables["fact_sales"].employee_id, tables["dim_employee"].employee_id),
        "fact_sales.store_id -> dim_store": (tables["fact_sales"].store_id, tables["dim_store"].store_id),
        "fact_sales.warehouse_id -> dim_warehouse": (tables["fact_sales"].warehouse_id, tables["dim_warehouse"].warehouse_id),
        "fact_sales.sale_date_key -> dim_date": (tables["fact_sales"].sale_date_key, tables["dim_date"].date_key),
        "fact_sales.delivery_date_key -> dim_date": (tables["fact_sales"].delivery_date_key, tables["dim_date"].date_key),
        "fact_returns.sale_id -> fact_sales": (tables["fact_returns"].sale_id, tables["fact_sales"].sale_id),
        "fact_returns.return_date_key -> dim_date": (tables["fact_returns"].return_date_key, tables["dim_date"].date_key),
        "fact_payments.sale_id -> fact_sales": (tables["fact_payments"].sale_id, tables["fact_sales"].sale_id),
        "fact_inventory.sale_id -> fact_sales": (tables["fact_inventory"].sale_id, tables["fact_sales"].sale_id),
        "fact_inventory.product_id -> dim_product": (tables["fact_inventory"].product_id, tables["dim_product"].product_id),
        "fact_inventory.warehouse_id -> dim_warehouse": (tables["fact_inventory"].warehouse_id, tables["dim_warehouse"].warehouse_id),
    }
    foreign_key_issues = {name: fk_missing(child, parent) for name, (child, parent) in fk_pairs.items()}
    sales = tables["fact_sales"]
    financial_issues = {
        "gross_amount": int((~np.isclose(sales.gross_amount, sales.quantity * sales.unit_price, atol=0.011, rtol=0)).sum()),
        "discount_amount": int((~np.isclose(sales.discount_amount, sales.gross_amount * sales.discount_pct, atol=0.011, rtol=0)).sum()),
        "net_amount": int((~np.isclose(sales.net_amount, sales.gross_amount - sales.discount_amount, atol=0.011, rtol=0)).sum()),
        "total_cost": int((~np.isclose(sales.total_cost, sales.quantity * sales.unit_cost, atol=0.011, rtol=0)).sum()),
        "margin_amount": int((~np.isclose(sales.margin_amount, sales.net_amount - sales.total_cost, atol=0.011, rtol=0)).sum()),
    }
    quantity_issues = {
        "sales_quantity_missing": int(sales.quantity.isna().sum()),
        "sales_quantity_non_positive": int((sales.quantity <= 0).sum()),
        "inventory_quantity_mismatch": int((tables["fact_inventory"].quantity_sold.to_numpy() != sales.quantity.to_numpy()).sum()),
        "inventory_stock_arithmetic": int((~np.isclose(
            tables["fact_inventory"].stock_after_sale,
            tables["fact_inventory"].stock_before_sale - tables["fact_inventory"].quantity_sold,
            atol=0.001,
            rtol=0,
        )).sum()),
    }
    date_dimension = tables["dim_date"]
    date_issues = {
        "date_key_missing": int(date_dimension.date_key.isna().sum()),
        "date_key_format_issues": int((~date_dimension.date_key.astype("string").str.fullmatch(r"20\d{6}", na=False)).sum()),
        "date_key_value_mismatch": int((pd.to_datetime(date_dimension.date, errors="coerce").dt.strftime("%Y%m%d").astype("Int64") != date_dimension.date_key).sum()),
        "fact_date_key_missing": int(sales[["sale_date_key", "delivery_date_key"]].isna().sum().sum()),
    }
    returns = tables["fact_returns"]
    return_net_amounts = sales.set_index("sale_id").loc[returns.sale_id, "net_amount"].to_numpy()
    return_issues = {
        "returned_flag_mismatch": int((sales.sale_id.isin(returns.sale_id) != sales.is_returned).sum()),
        "return_date_missing": int(returns.return_date_key.isna().sum()),
        "refund_above_net_amount": int((returns.refund_amount > return_net_amounts + 0.011).sum()),
    }
    payments = tables["fact_payments"]
    payment_issues = {
        "payment_amount_mismatch": int((~np.isclose(payments.payment_amount, sales.net_amount, atol=0.011, rtol=0)).sum()),
        "payment_status_missing": int(payments.payment_status.isna().sum()),
    }
    inventory = tables["fact_inventory"]
    inventory_issues = {
        "inventory_sale_alignment": int((inventory.sale_id.to_numpy() != sales.sale_id.to_numpy()).sum()),
        "negative_stock": int(((inventory.stock_before_sale < 0) | (inventory.stock_after_sale < 0)).sum()),
        "stock_value_missing": int(inventory[["stock_before_sale", "stock_after_sale"]].isna().sum().sum()),
    }
    completeness_issues = {
        "fact_sales_row_difference_vs_silver": abs(len(sales) - silver_rows),
        "payment_row_difference_vs_sales": abs(len(tables["fact_payments"]) - len(sales)),
        "inventory_row_difference_vs_sales": abs(len(tables["fact_inventory"]) - len(sales)),
        "returns_not_matching_returned_sales": abs(len(tables["fact_returns"]) - int(sales.is_returned.sum())),
    }
    issue_groups = (primary_key_issues, foreign_key_issues, financial_issues, quantity_issues, date_issues, return_issues, payment_issues, inventory_issues, completeness_issues)
    passed = all(value == 0 for group in issue_groups for value in group.values())
    return {
        "primary_key_issues": primary_key_issues,
        "foreign_key_issues": foreign_key_issues,
        "financial_issues": financial_issues,
        "quantity_issues": quantity_issues,
        "date_issues": date_issues,
        "return_issues": return_issues,
        "payment_issues": payment_issues,
        "inventory_issues": inventory_issues,
        "completeness_issues": completeness_issues,
        "passed": passed,
    }


def report(tables: dict[str, pd.DataFrame], checks: dict[str, Any]) -> str:
    metadata = {
        "dim_customer": ("customer_id", "—"),
        "dim_product": ("product_id", "supplier_id → dim_supplier"),
        "dim_supplier": ("supplier_id", "—"),
        "dim_employee": ("employee_id", "—"),
        "dim_store": ("store_id", "—"),
        "dim_warehouse": ("warehouse_id", "store_id → dim_store"),
        "dim_date": ("date_key", "—"),
        "fact_sales": ("sale_id", "customer_id, product_id, employee_id, store_id, warehouse_id, sale_date_key, delivery_date_key"),
        "fact_returns": ("sale_id", "sale_id → fact_sales; return_date_key → dim_date"),
        "fact_payments": ("sale_id", "sale_id → fact_sales"),
        "fact_inventory": ("sale_id", "sale_id → fact_sales; product_id → dim_product; warehouse_id → dim_warehouse"),
    }
    lines = ["# TechStore — Transformation Report", "", "## Tables produites", "", "| Table | Lignes | Colonnes | Clé primaire | Clés étrangères |", "|---|---:|---:|---|---|"]
    for name, frame in tables.items():
        primary_key, foreign_keys = metadata[name]
        lines.append(f"| `{name}` | {len(frame):,} | {len(frame.columns)} | `{primary_key}` | {foreign_keys} |")
    lines.extend([
        "", "## Grain", "",
        "- `fact_sales` : une ligne par transaction (`sale_id`).",
        "- `fact_returns` : une ligne par transaction retournée.",
        "- `fact_payments` : une ligne de paiement par transaction ; aucune clé de paiement distincte n’existe dans la source.",
        "- `fact_inventory` : un mouvement/état de stock par transaction, produit et entrepôt.",
        "", "## Affectation des colonnes", "",
        "- Client : identité et segmentation dans `dim_customer`; `customer_age` reste dans `fact_sales`, car il varie dans le temps.",
        "- Produit et fournisseur : descriptifs dans leurs dimensions, avec `supplier_id` porté par `dim_product`.",
        "- Magasin, employé et entrepôt : descriptifs dans les dimensions; l’entrepôt est relié de façon univoque au magasin.",
        "- Dates : `sale_date`, `delivery_date` et `return_date` deviennent des clés vers `dim_date`; les attributs calendrier Silver ne sont pas recopiés dans les faits.",
        "- Paiement : méthode, statut, devise et montant net dans `fact_payments`.",
        "- Retour : motif, date et remboursement dans `fact_returns` uniquement.",
        "- Stock : stocks avant/après et quantité vendue dans `fact_inventory` uniquement.",
        "", "## Colonnes non recopiées ou déplacées", "",
        "- Aucune colonne Silver n’est abandonnée sans justification : chaque champ est placé dans une dimension, un fait, ou est reconstitué depuis `dim_date`.",
        "- `sale_year`, `sale_month`, `sale_day`, `sale_quarter` et `sale_weekday` ne sont pas recopiés : ils sont calculés une seule fois dans `dim_date`.",
        "- Les attributs client, produit, fournisseur, magasin et employé ne sont pas répétés dans les faits : seules leurs clés y sont conservées.",
        "- Les champs de retour, paiement et stock vivent exclusivement dans leurs tables de faits spécialisées; `is_returned` reste dans `fact_sales` comme indicateur analytique.",
        "", "## Contrôles de qualité", "", f"- Statut global : **{'PASS' if checks['passed'] else 'REVIEW'}**",
    ])
    for section in ("primary_key_issues", "foreign_key_issues", "financial_issues", "quantity_issues", "date_issues", "return_issues", "payment_issues", "inventory_issues", "completeness_issues"):
        lines.extend(["", f"### {section.replace('_', ' ').title()}", ""])
        lines.extend(f"- {name}: {count:,}" for name, count in checks[section].items())
    lines.extend(["", "## Problèmes rencontrés", "", "- Aucun conflit d’attributs pour les dimensions créées.", "- L’âge client n’est pas placé dans `dim_customer` afin d’éviter une duplication temporelle; il est conservé au grain de vente.", ""])
    return "\n".join(lines)


def main() -> None:
    if not SILVER_FILE.exists():
        raise FileNotFoundError(f"Dataset Silver introuvable : {SILVER_FILE}")
    source = pd.read_csv(SILVER_FILE, parse_dates=["sale_date", "delivery_date", "return_date"], low_memory=False)
    source = add_date_keys(source)

    tables: dict[str, pd.DataFrame] = {}
    tables["dim_customer"] = distinct(source, ["customer_id", "customer_full_name", "customer_email", "customer_gender", "customer_city", "customer_segment"], "customer_id")
    tables["dim_supplier"] = distinct(source, ["supplier_id", "supplier_name", "supplier_country"], "supplier_id")
    tables["dim_product"] = distinct(source, ["product_id", "product_name", "product_category", "product_subcategory", "product_brand", "product_warranty_months", "supplier_id"], "product_id")
    tables["dim_employee"] = distinct(source, ["employee_id", "employee_full_name", "employee_role"], "employee_id")
    tables["dim_store"] = distinct(source, ["store_id", "store_name", "store_city", "store_country", "store_region", "store_type"], "store_id")
    tables["dim_warehouse"] = distinct(source, ["warehouse_id", "store_id"], "warehouse_id")
    tables["dim_date"] = date_dimension(source)

    tables["fact_sales"] = source[[
        "sale_id", "sale_date_key", "delivery_date_key", "customer_id", "product_id", "employee_id", "store_id", "warehouse_id",
        "quantity", "unit_price", "unit_cost", "discount_pct", "gross_amount", "discount_amount", "net_amount", "total_cost",
        "margin_amount", "margin_pct", "sales_channel", "delivery_method", "shipping_cost", "shipping_cost_imputed", "order_status",
        "is_returned", "customer_satisfaction_score", "customer_age", "customer_age_imputed",
    ]].copy()
    tables["fact_returns"] = source.loc[source["is_returned"], ["sale_id", "return_date_key", "return_reason", "refund_amount"]].copy()
    tables["fact_payments"] = source[["sale_id", "payment_method", "payment_status", "currency", "net_amount"]].rename(columns={"net_amount": "payment_amount"}).copy()
    tables["fact_inventory"] = source[["sale_id", "product_id", "warehouse_id", "quantity", "stock_before_sale", "stock_after_sale"]].rename(columns={"quantity": "quantity_sold"}).copy()

    checks = quality_checks(tables, len(source))
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(GOLD_DIR / f"{name}.csv", index=False, encoding="utf-8")
    (GOLD_DIR / "transformation_quality_checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    REPORT_FILE.write_text(report(tables, checks), encoding="utf-8")
    print(f"Created {len(tables)} Gold tables in {GOLD_DIR}")
    print(f"Quality status: {'PASS' if checks['passed'] else 'REVIEW'}")


if __name__ == "__main__":
    main()
