"""Build the TechStore Silver dataset from the immutable RAW CSV.

The script never writes into data/raw. It produces the cleaned CSV, a JSON audit
trail and a Markdown report in the project Silver/documentation layers.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
REPORT_DIR = PROJECT_ROOT / "docs" / "reports"
ID_PATTERNS = {
    "sale_id": r"TRX\d{7}",
    "store_id": r"STR\d{3}",
    "employee_id": r"EMP\d{4}",
    "customer_id": r"CUS\d{5}",
    "product_id": r"PRD\d{4}",
    "supplier_id": r"SUP\d{3}",
    "warehouse_id": r"WH\d{3}",
}
DATE_COLUMNS = ["sale_date", "delivery_date", "return_date"]
REQUIRED_COLUMNS = ["sale_id", "sale_date", "store_id", "customer_id", "product_id", "quantity", "net_amount"]
FINANCIAL_RULES = {
    "gross_amount": lambda d: d["quantity"] * d["unit_price"],
    "discount_amount": lambda d: d["gross_amount"] * d["discount_pct"],
    "net_amount": lambda d: d["gross_amount"] - d["discount_amount"],
    "total_cost": lambda d: d["quantity"] * d["unit_cost"],
    "margin_amount": lambda d: d["net_amount"] - d["total_cost"],
}


def find_raw_csv(input_path: str | None) -> Path:
    if input_path:
        path = Path(input_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Fichier RAW introuvable : {path}")
        return path
    files = sorted(RAW_DIR.glob("*.csv"))
    if len(files) != 1:
        raise ValueError("data/raw doit contenir un unique CSV ; utilisez --input sinon.")
    return files[0]


def normalize_text(value: object) -> object:
    """Normalise Unicode and whitespace without changing semantic casing."""
    if not isinstance(value, str):
        return value
    normalized = unicodedata.normalize("NFKC", value)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized if normalized else pd.NA


def serialize(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def quality_checks(dataframe: pd.DataFrame) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    checks["exact_duplicate_rows"] = int(dataframe.duplicated().sum())
    checks["duplicate_sale_ids"] = int(dataframe["sale_id"].duplicated().sum())
    checks["required_field_missing"] = {
        column: int(dataframe[column].isna().sum()) for column in REQUIRED_COLUMNS
    }
    checks["invalid_identifiers"] = {
        column: int((~dataframe[column].astype("string").str.fullmatch(pattern, na=False)).sum())
        for column, pattern in ID_PATTERNS.items()
    }
    checks["date_issues"] = {
        "delivery_before_sale": int((dataframe["delivery_date"] < dataframe["sale_date"]).sum()),
        "return_before_sale": int((dataframe["return_date"] < dataframe["sale_date"]).sum()),
        "sale_year_mismatch": int((dataframe["sale_year"] != dataframe["sale_date"].dt.year).sum()),
        "sale_month_mismatch": int((dataframe["sale_month"] != dataframe["sale_date"].dt.month).sum()),
        "sale_day_mismatch": int((dataframe["sale_day"] != dataframe["sale_date"].dt.day).sum()),
    }
    checks["business_rule_issues"] = {
        "non_positive_quantity": int((dataframe["quantity"] <= 0).sum()),
        "negative_unit_price_or_cost": int(((dataframe["unit_price"] < 0) | (dataframe["unit_cost"] < 0)).sum()),
        "discount_outside_0_1": int(((dataframe["discount_pct"] < 0) | (dataframe["discount_pct"] > 1)).sum()),
        "negative_shipping_cost": int((dataframe["shipping_cost"] < 0).sum()),
        "customer_age_outside_16_100": int(((dataframe["customer_age"] < 16) | (dataframe["customer_age"] > 100)).sum()),
        "negative_stock": int(((dataframe["stock_before_sale"] < 0) | (dataframe["stock_after_sale"] < 0)).sum()),
        "stock_mismatch": int(
            (dataframe["stock_after_sale"] != dataframe["stock_before_sale"] - dataframe["quantity"]).sum()
        ),
        "returned_without_date": int(((dataframe["is_returned"]) & dataframe["return_date"].isna()).sum()),
        "returned_without_reason": int(((dataframe["is_returned"]) & dataframe["return_reason"].isna()).sum()),
        "non_returned_with_return_date": int((~dataframe["is_returned"] & dataframe["return_date"].notna()).sum()),
        "invalid_return_refund": int(
            ((dataframe["is_returned"]) & ((dataframe["refund_amount"] < 0) | (dataframe["refund_amount"] > dataframe["net_amount"] + 0.011))).sum()
        ),
        "score_outside_1_5": int(
            ((dataframe["customer_satisfaction_score"] < 1) | (dataframe["customer_satisfaction_score"] > 5)).sum()
        ),
    }
    checks["financial_calculation_issues"] = {
        name: int((~np.isclose(dataframe[name], formula(dataframe), atol=0.011, rtol=0)).sum())
        for name, formula in FINANCIAL_RULES.items()
    }
    checks["financial_calculation_issues"]["margin_pct"] = int(
        (~np.isclose(dataframe["margin_pct"], dataframe["margin_amount"] / dataframe["net_amount"], atol=0.001, rtol=0)).sum()
    )
    issues = json.dumps(checks)
    checks["passed"] = not bool(re.search(r":\s*[1-9]\d*", issues))
    return checks


def render_report(audit: dict[str, Any], checks: dict[str, Any]) -> str:
    lines = [
        "# TechStore — Cleaning Report",
        "",
        f"- Exécuté (UTC) : {audit['executed_at_utc']}",
        f"- Source RAW (lecture seule) : `{audit['source_file']}`",
        f"- Lignes avant nettoyage : {audit['rows_before']:,}",
        f"- Lignes après nettoyage : {audit['rows_after']:,}",
        "",
        "## Corrections appliquées",
        "",
    ]
    for name, count in audit["corrections"].items():
        lines.append(f"- {name} : {count:,}")
    lines.extend(["", "## Contrôles de qualité Silver", "", f"- Statut global : **{'PASS' if checks['passed'] else 'REVIEW'}**"])
    for section in ("required_field_missing", "invalid_identifiers", "date_issues", "business_rule_issues", "financial_calculation_issues"):
        lines.extend(["", f"### {section.replace('_', ' ').title()}", ""])
        lines.extend(f"- {key}: {value:,}" for key, value in checks[section].items())
    lines.extend([
        "",
        "## Décisions métier",
        "",
        "- Les champs `return_reason` et `return_date` restent nulls pour les ventes non retournées : c’est une absence métier légitime.",
        "- Les scores de satisfaction absents restent nulls ; aucun score n’est inventé.",
        "- Les âges manquants sont imputés par la médiane globale et signalés par `customer_age_imputed`.",
        "- Les frais de livraison manquants sont imputés par la médiane de leur méthode de livraison et signalés par `shipping_cost_imputed`.",
        "- Les valeurs extrêmes sont contrôlées, mais ne sont pas supprimées automatiquement sans règle métier approuvée.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean TechStore RAW data into the Silver layer.")
    parser.add_argument("--input", help="Optional RAW CSV path; default is the unique CSV in data/raw.")
    args = parser.parse_args()

    source = find_raw_csv(args.input)
    dataframe = pd.read_csv(source, low_memory=False)
    audit: dict[str, Any] = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(source),
        "rows_before": int(len(dataframe)),
        "corrections": {},
    }

    text_columns = dataframe.select_dtypes(include=["object", "string"]).columns.tolist()
    before_text = dataframe[text_columns].copy()
    dataframe[text_columns] = dataframe[text_columns].apply(lambda col: col.map(normalize_text))
    text_changed = (
        before_text.isna() ^ dataframe[text_columns].isna()
    ) | (
        before_text.notna()
        & dataframe[text_columns].notna()
        & before_text.ne(dataframe[text_columns])
    )
    audit["corrections"]["text_values_normalized"] = int(text_changed.sum().sum())

    for column in DATE_COLUMNS:
        original_not_null = dataframe[column].notna()
        dataframe[column] = pd.to_datetime(dataframe[column], errors="coerce")
        audit["corrections"][f"invalid_{column}_converted_to_null"] = int((original_not_null & dataframe[column].isna()).sum())

    duplicate_rows = int(dataframe.duplicated().sum())
    dataframe = dataframe.drop_duplicates().copy()
    duplicate_ids = int(dataframe["sale_id"].duplicated(keep="first").sum())
    dataframe = dataframe.drop_duplicates(subset=["sale_id"], keep="first").copy()
    audit["corrections"]["exact_duplicate_rows_removed"] = duplicate_rows
    audit["corrections"]["duplicate_sale_ids_removed"] = duplicate_ids

    dataframe["customer_age"] = pd.to_numeric(dataframe["customer_age"], errors="coerce")
    invalid_age = (dataframe["customer_age"] < 16) | (dataframe["customer_age"] > 100)
    dataframe.loc[invalid_age, "customer_age"] = np.nan
    dataframe["customer_age_imputed"] = dataframe["customer_age"].isna()
    dataframe["customer_age"] = dataframe["customer_age"].fillna(dataframe["customer_age"].median()).round().astype("Int64")
    audit["corrections"]["invalid_customer_ages_converted_to_null"] = int(invalid_age.sum())
    audit["corrections"]["customer_ages_imputed"] = int(dataframe["customer_age_imputed"].sum())

    dataframe["shipping_cost"] = pd.to_numeric(dataframe["shipping_cost"], errors="coerce")
    invalid_shipping = dataframe["shipping_cost"] < 0
    dataframe.loc[invalid_shipping, "shipping_cost"] = np.nan
    dataframe["shipping_cost_imputed"] = dataframe["shipping_cost"].isna()
    dataframe["shipping_cost"] = dataframe["shipping_cost"].fillna(
        dataframe.groupby("delivery_method")["shipping_cost"].transform("median")
    )
    audit["corrections"]["negative_shipping_costs_converted_to_null"] = int(invalid_shipping.sum())
    audit["corrections"]["shipping_costs_imputed"] = int(dataframe["shipping_cost_imputed"].sum())

    for column, formula in FINANCIAL_RULES.items():
        expected = formula(dataframe).round(2)
        mismatch = ~np.isclose(dataframe[column], expected, atol=0.011, rtol=0)
        dataframe.loc[mismatch, column] = expected[mismatch]
        audit["corrections"][f"{column}_recalculated"] = int(mismatch.sum())
    expected_margin_pct = (dataframe["margin_amount"] / dataframe["net_amount"]).round(3)
    margin_pct_mismatch = ~np.isclose(dataframe["margin_pct"], expected_margin_pct, atol=0.001, rtol=0)
    dataframe.loc[margin_pct_mismatch, "margin_pct"] = expected_margin_pct[margin_pct_mismatch]
    audit["corrections"]["margin_pct_recalculated"] = int(margin_pct_mismatch.sum())

    audit["rows_after"] = int(len(dataframe))
    checks = quality_checks(dataframe)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(SILVER_DIR / "techstore_cleaned.csv", index=False, encoding="utf-8")
    (SILVER_DIR / "cleaning_audit.json").write_text(json.dumps(audit, indent=2, default=serialize), encoding="utf-8")
    (SILVER_DIR / "quality_checks.json").write_text(json.dumps(checks, indent=2, default=serialize), encoding="utf-8")
    (REPORT_DIR / "cleaning_report.md").write_text(render_report(audit, checks), encoding="utf-8")
    print(f"Silver dataset created: {SILVER_DIR / 'techstore_cleaned.csv'}")
    print(f"Quality status: {'PASS' if checks['passed'] else 'REVIEW'}")


if __name__ == "__main__":
    main()
