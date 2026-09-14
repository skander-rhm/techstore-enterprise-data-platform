"""Profile the immutable TechStore RAW CSV without altering it.

Usage:
    python src/quality/profile_dataset.py
    python src/quality/profile_dataset.py --input data/raw/techstore_dataset.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = PROJECT_ROOT / "docs" / "reports"


def find_source_csv(input_path: str | None) -> Path:
    """Resolve an explicitly supplied CSV or the unique CSV in data/raw."""
    if input_path:
        source = Path(input_path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"CSV introuvable : {source}")
        return source

    candidates = sorted((PROJECT_ROOT / "data" / "raw").glob("*.csv"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError("Aucun CSV trouvé dans data/raw. Utilisez --input.")
    raise ValueError("Plusieurs CSV trouvés dans data/raw. Utilisez --input.")


def calculate_profile(dataframe: pd.DataFrame, source: Path) -> dict[str, Any]:
    """Return a serialisable, read-only structural profile of a dataframe."""
    rows, columns = dataframe.shape
    missing = dataframe.isna().sum()
    return {
        "source_file": str(source),
        "rows": rows,
        "columns": columns,
        "exact_duplicate_rows": int(dataframe.duplicated().sum()),
        "columns_profile": [
            {
                "column": column,
                "dtype": str(dataframe[column].dtype),
                "non_null_count": int(dataframe[column].notna().sum()),
                "missing_count": int(missing[column]),
                "missing_pct": round(float(missing[column] / rows * 100), 2),
                "distinct_count": int(dataframe[column].nunique(dropna=True)),
                "sample_values": [str(value) for value in dataframe[column].dropna().head(3)],
            }
            for column in dataframe.columns
        ],
    }


def markdown_report(profile: dict[str, Any]) -> str:
    """Render the JSON profile as a concise Markdown report."""
    lines = [
        "# TechStore — Dataset Profiling Report",
        "",
        f"- Source: `{profile['source_file']}`",
        f"- Rows: {profile['rows']:,}",
        f"- Columns: {profile['columns']}",
        f"- Exact duplicate rows: {profile['exact_duplicate_rows']:,}",
        "",
        "| Column | Type | Non-null | Missing | Missing % | Distinct | Sample values |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for column in profile["columns_profile"]:
        samples = ", ".join(column["sample_values"]).replace("|", "\\|")
        lines.append(
            "| {column} | {dtype} | {non_null_count:,} | {missing_count:,} | "
            "{missing_pct:.2f}% | {distinct_count:,} | {samples} |".format(
                samples=samples, **column
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a TechStore RAW CSV without modifying it.")
    parser.add_argument("--input", help="Path to the source CSV. Defaults to the unique file in data/raw.")
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_REPORT_DIR,
        type=Path,
        help="Directory for Markdown and JSON reports (default: docs/reports).",
    )
    args = parser.parse_args()

    source = find_source_csv(args.input)
    dataframe = pd.read_csv(source, low_memory=False)
    profile = calculate_profile(dataframe, source)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "dataset_profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output_dir / "dataset_profile.md").write_text(markdown_report(profile), encoding="utf-8")
    print(f"Profiling terminé : {args.output_dir / 'dataset_profile.md'}")


if __name__ == "__main__":
    main()
