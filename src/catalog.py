"""Named queries used by both the dashboard API and the MCP server.

Keep this file as the single place that talks to DuckDB. If you add a new
question to "Ask the data", add a function here and register it in TOOLS.
"""

from __future__ import annotations

from typing import Any, Callable

import duckdb

from src.paths import WAREHOUSE_PATH


def connect():
    if not WAREHOUSE_PATH.exists():
        raise FileNotFoundError(
            "Warehouse not found. From the repo root run:\n"
            "  python scripts/generate_omop_sample.py\n"
            "  python scripts/build_warehouse.py"
        )
    return duckdb.connect(str(WAREHOUSE_PATH), read_only=True)


def _rows(sql: str, params: list | None = None) -> list[dict[str, Any]]:
    con = connect()
    try:
        result = con.execute(sql, params or [])
        columns = [d[0] for d in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    finally:
        con.close()


def get_overview() -> dict[str, Any]:
    stats = _rows(
        """
        select
            count(*) as patients,
            round(100.0 * avg(has_t2dm), 1) as t2dm_pct,
            round(100.0 * avg(has_hypertension), 1) as htn_pct,
            round(100.0 * avg(has_obesity), 1) as obesity_pct,
            sum(visit_count) as visits,
            sum(er_visit_count) as er_visits
        from mart_patient_cohort
        """
    )[0]
    quality = _rows("select sum(issue_count) as issues from mart_data_quality")[0]
    stats["data_quality_issues"] = quality["issues"]
    return stats


def get_cohort_summary() -> list[dict[str, Any]]:
    return _rows(
        """
        select
            count(*) as patients,
            sum(has_t2dm) as t2dm,
            sum(has_hypertension) as hypertension,
            sum(has_obesity) as obesity,
            sum(has_ckd) as ckd,
            sum(has_influenza) as influenza,
            sum(on_metformin) as metformin,
            sum(on_lisinopril) as lisinopril
        from mart_patient_cohort
        """
    )


def get_condition_trends() -> list[dict[str, Any]]:
    return _rows(
        """
        select year, condition_name, condition_events, unique_patients
        from mart_condition_trends
        order by year, condition_events desc
        """
    )


def get_county_prevalence() -> list[dict[str, Any]]:
    return _rows("select * from mart_county_prevalence")


def get_data_quality() -> list[dict[str, Any]]:
    return _rows("select * from mart_data_quality order by issue_count desc")


def lookup_patients(
    condition: str | None = None,
    county: str | None = None,
    limit: int = 25,
) -> list[dict[str, Any]]:
    where = ["1=1"]
    params: list[Any] = []
    flag = {
        "diabetes": "has_t2dm = 1",
        "t2dm": "has_t2dm = 1",
        "hypertension": "has_hypertension = 1",
        "htn": "has_hypertension = 1",
        "obesity": "has_obesity = 1",
        "ckd": "has_ckd = 1",
        "influenza": "has_influenza = 1",
        "flu": "has_influenza = 1",
    }
    if condition:
        key = condition.strip().lower()
        if key in flag:
            where.append(flag[key])
    if county:
        where.append("lower(county) like ?")
        params.append(f"%{county.strip().lower()}%")
    limit = max(1, min(int(limit), 100))
    sql = f"""
        select person_id, age_years, gender, race, county, state,
               has_t2dm, has_hypertension, has_obesity, has_ckd, has_influenza,
               visit_count, er_visit_count, on_metformin, on_lisinopril
        from mart_patient_cohort
        where {' and '.join(where)}
        order by person_id
        limit {limit}
    """
    return _rows(sql, params)


def t2dm_with_er() -> list[dict[str, Any]]:
    return _rows(
        """
        select
            count(*) as t2dm_patients,
            sum(case when er_visit_count > 0 then 1 else 0 end) as with_er_visit,
            round(100.0 * avg(case when er_visit_count > 0 then 1.0 else 0 end), 1) as pct_with_er
        from mart_patient_cohort
        where has_t2dm = 1
        """
    )


def metformin_coverage() -> list[dict[str, Any]]:
    return _rows(
        """
        select
            sum(has_t2dm) as t2dm_patients,
            sum(case when has_t2dm = 1 and on_metformin = 1 then 1 else 0 end) as on_metformin,
            round(
                100.0 * sum(case when has_t2dm = 1 and on_metformin = 1 then 1 else 0 end)
                / nullif(sum(has_t2dm), 0),
                1
            ) as coverage_pct
        from mart_patient_cohort
        """
    )


TOOLS: dict[str, dict[str, Any]] = {
    "get_overview": {
        "title": "Cohort overview",
        "description": "Patient counts and chronic-disease percentages for the synthetic OMOP mart.",
        "fn": lambda **_: get_overview(),
    },
    "get_cohort_summary": {
        "title": "Condition and medication counts",
        "description": "How many patients have T2DM, hypertension, obesity, CKD, influenza, and common drugs.",
        "fn": lambda **_: get_cohort_summary(),
    },
    "get_condition_trends": {
        "title": "Condition trends by year",
        "description": "Yearly condition event counts from condition_occurrence.",
        "fn": lambda **_: get_condition_trends(),
    },
    "get_county_prevalence": {
        "title": "County prevalence",
        "description": "T2DM, hypertension, obesity, and ER use by U.S. county in the sample.",
        "fn": lambda **_: get_county_prevalence(),
    },
    "get_data_quality": {
        "title": "Data quality checks",
        "description": "Orphan keys, future dates, and other CDM hygiene flags.",
        "fn": lambda **_: get_data_quality(),
    },
    "lookup_patients": {
        "title": "Patient lookup table",
        "description": "Filter the person-level mart by condition and county. No PHI — synthetic IDs only.",
        "fn": lambda condition=None, county=None, limit=25, **_: lookup_patients(
            condition=condition, county=county, limit=limit
        ),
    },
    "t2dm_with_er": {
        "title": "Type 2 diabetes with ER use",
        "description": "Share of T2DM patients who had at least one emergency visit.",
        "fn": lambda **_: t2dm_with_er(),
    },
    "metformin_coverage": {
        "title": "Metformin coverage in T2DM",
        "description": "How many T2DM patients have a metformin drug_exposure.",
        "fn": lambda **_: metformin_coverage(),
    },
}


def run_tool(name: str, **kwargs: Any) -> Any:
    if name not in TOOLS:
        raise KeyError(f"Unknown tool: {name}. Try one of: {', '.join(TOOLS)}")
    fn: Callable = TOOLS[name]["fn"]
    return fn(**kwargs)


def list_tools() -> list[dict[str, str]]:
    return [
        {"name": name, "title": spec["title"], "description": spec["description"]}
        for name, spec in TOOLS.items()
    ]
