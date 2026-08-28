"""Tiny rule-based question router.

No API key. Questions map onto the same named tools the MCP server exposes.
This is enough to demo "ask the data" in an interview without a hosted LLM.
"""

from __future__ import annotations

import re
from typing import Any

from src.catalog import list_tools, run_tool

EXAMPLES = [
    "How many patients are in the cohort?",
    "What is hypertension prevalence by county?",
    "Show data quality issues",
    "Metformin coverage for diabetes",
    "Lookup diabetes patients in San Francisco",
    "Condition trends by year",
    "Type 2 diabetes patients with ER visits",
    "Find T2DM patients in Alameda taking metformin",
    "Find T2DM patients in Alameda taking metformin aged 60 to 70",
]


def _contains(text: str, *needles: str) -> bool:
    return any(n in text for n in needles)


def route(question: str) -> dict[str, Any]:
    q = re.sub(r"\s+", " ", question.strip().lower())
    if not q:
        return {
            "matched_tool": None,
            "message": "Ask a question about the cohort, counties, quality, or medications.",
            "examples": EXAMPLES,
            "result": None,
        }

    county = None
    for name in [
        "san francisco",
        "santa clara",
        "baltimore",
        "alameda",
        "montgomery",
        "los angeles",
    ]:
        if name in q:
            county = name.title() if name != "san francisco" else "San Francisco"
            if name == "los angeles":
                county = "Los Angeles"
            if name == "santa clara":
                county = "Santa Clara"
            break

    min_age = None
    max_age = None

    age_range = re.search(r"(?:age(?:d)?\s*)?(\d{1,3})\s*(?:-|to)\s*(\d{1,3})", q)
    if age_range:
        min_age = int(age_range.group(1))
        max_age = int(age_range.group(2))

    condition = None
    if _contains(q, "diabetes", "t2dm", "type 2"):
        condition = "diabetes"
    elif _contains(q, "hypertension", "htn", "blood pressure"):
        condition = "hypertension"
    elif _contains(q, "obesity"):
        condition = "obesity"
    elif _contains(q, "kidney", "ckd"):
        condition = "ckd"
    elif _contains(q, "influenza", "flu"):
        condition = "influenza"

    medication = None
    if _contains(q, "metformin"):
        medication = "metformin"
    elif _contains(q, "lisinopril"):
        medication = "lisinopril"

    if (
        condition
        and ("find" in q or "build" in q or "cohort" in q)
        and (county or medication or min_age is not None or max_age is not None)
    ):
        tool, args = "build_research_cohort", {
            "condition": condition,
            "county": county,
            "medication": medication,
            "min_age": min_age,
            "max_age": max_age,
        }

    elif _contains(q, "lookup", "list patients", "show patients", "table"):
        tool, args = "lookup_patients", {"condition": condition, "county": county, "limit": 25}
    elif _contains(q, "quality", "orphan", "future date", "data issue"):
        tool, args = "get_data_quality", {}
    elif _contains(q, "county", "prevalence", "geographic", "fips"):
        tool, args = "get_county_prevalence", {}
    elif _contains(q, "trend", "by year", "over time"):
        tool, args = "get_condition_trends", {}
    elif _contains(q, "metformin", "coverage", "drug"):
        tool, args = "metformin_coverage", {}
    elif (_contains(q, "emergency", "emergency room", "er visit", "er visits") and _contains(q, "diabetes", "t2dm", "type 2")):
        tool, args = "t2dm_with_er", {}
    elif _contains(q, "how many", "overview", "summary", "cohort"):
        tool, args = "get_overview", {}
    elif condition and county:
        tool, args = "lookup_patients", {"condition": condition, "county": county, "limit": 25}
    elif condition:
        tool, args = "get_cohort_summary", {}
    else:
        tool, args = "get_overview", {}

    result = run_tool(tool, **args)
    return {
        "question": question,
        "matched_tool": tool,
        "args": args,
        "message": f"Routed to `{tool}` (same function the MCP server uses).",
        "examples": EXAMPLES,
        "available_tools": list_tools(),
        "result": result,
    }
