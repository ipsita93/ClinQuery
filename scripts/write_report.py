#!/usr/bin/env python3
"""Write a short findings report from the marts (same queries as the dashboard)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.catalog import (  # noqa: E402
    get_county_prevalence,
    get_data_quality,
    get_overview,
    metformin_coverage,
    t2dm_with_er,
)
from src.paths import REPORTS_DIR  # noqa: E402


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ov = get_overview()
    counties = get_county_prevalence()
    quality = get_data_quality()
    er = t2dm_with_er()[0]
    met = metformin_coverage()[0]

    lines = [
        "# Sample findings (synthetic OMOP mart)",
        "",
        f"_Generated {date.today().isoformat()}. Not real patients. Not for clinical use._",
        "",
        "## Cohort snapshot",
        "",
        f"- **{ov['patients']}** synthetic patients, **{ov['visits']}** visits, **{ov['er_visits']}** ER visits.",
        f"- Type 2 diabetes: **{ov['t2dm_pct']}%**. Hypertension: **{ov['htn_pct']}%**. Obesity: **{ov['obesity_pct']}%**.",
        f"- Among T2DM patients, **{er['pct_with_er']}%** had at least one ER visit.",
        f"- Metformin recorded for **{met['coverage_pct']}%** of T2DM patients.",
        "",
        "## County prevalence",
        "",
        "| County | State | Patients | T2DM % | HTN % | Mean ER visits |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in counties:
        lines.append(
            f"| {row['county']} | {row['state']} | {row['patients']} | "
            f"{row['t2dm_pct']} | {row['htn_pct']} | {row['mean_er_visits']} |"
        )
    lines += [
        "",
        "## Data quality (intentional flags in the sample)",
        "",
        "| Check | Description | Issues |",
        "| --- | --- | --- |",
    ]
    for row in quality:
        lines.append(f"| `{row['check_name']}` | {row['description']} | {row['issue_count']} |")
    lines += [
        "",
        "## How to talk about this in an interview",
        "",
        "This is the kind of mart a data manager would hand a methods PI: person-grain flags,",
        "a geographic rollup for public health, and a short quality appendix before anyone",
        "fits a model. The dashboard and MCP `ask_data` tool read these same tables.",
        "",
    ]
    path = REPORTS_DIR / "sample_findings.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
