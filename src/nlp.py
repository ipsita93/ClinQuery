"""Tiny rule-based question router.

No API key. Questions map onto the same named tools the MCP server exposes.

This is enough to demo "ask the data" in an interview without a hosted LLM.
"""

from __future__ import annotations

import re
from typing import Any

from src.catalog import list_tools, run_tool


EXAMPLES = [
    "Find T2DM patients in Alameda taking metformin",
    "Find T2DM patients in Alameda taking metformin aged 60 to 70",
    "Find hypertension patients in San Francisco taking lisinopril",
    "Find hypertension patients in Santa Clara taking lisinopril aged 50 to 65",
    "Find diabetes patients in Alameda taking lisinopril",
    "Find T2DM patients in San Francisco",
    "Find hypertension patients in Alameda",
    "Find obesity patients in San Francisco",
    "Find CKD patients in Alameda",
    "Find diabetes patients in Santa Clara taking metformin",
    "Find T2DM patients in San Francisco aged 60 to 70",
]


def _contains(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _extract_county(q: str) -> str | None:
    counties = [
        "san francisco",
        "santa clara",
        "baltimore",
        "alameda",
        "montgomery",
        "los angeles",
    ]

    for name in counties:
        if name in q:
            return name.title()

    return None


def _extract_age_range(q: str) -> tuple[int | None, int | None]:
    patterns = [
        r"\bage\s+(\d{1,3})\s*(?:-|to)\s*(\d{1,3})\b",
        r"\baged\s+(\d{1,3})\s*(?:-|to)\s*(\d{1,3})\b",
        r"\b(\d{1,3})\s*(?:-|to)\s*(\d{1,3})\s*(?:years?\s*)?(?:old)?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, q)
        if match:
            return int(match.group(1)), int(match.group(2))

    return None, None


def _extract_condition(q: str) -> str | None:
    if _contains(q, "diabetes", "t2dm", "type 2"):
        return "diabetes"

    if _contains(q, "hypertension", "htn", "blood pressure"):
        return "hypertension"

    if _contains(q, "obesity"):
        return "obesity"

    if _contains(q, "kidney", "ckd"):
        return "ckd"

    if _contains(q, "influenza", "flu"):
        return "influenza"

    return None


def _extract_medication(q: str) -> str | None:
    if "metformin" in q:
        return "metformin"

    if "lisinopril" in q:
        return "lisinopril"

    return None


def route(question: str) -> dict[str, Any]:
    q = re.sub(r"\s+", " ", question.strip().lower())

    if not q:
        return {
            "question": question,
            "matched_tool": None,
            "args": {},
            "message": "Ask a question about the cohort, counties, quality, or medications.",
            "examples": EXAMPLES,
            "available_tools": list_tools(),
            "result": None,
        }

    county = _extract_county(q)
    min_age, max_age = _extract_age_range(q)
    condition = _extract_condition(q)
    medication = _extract_medication(q)

    # ---------------------------------------------------------
    # 1. Specific research cohort questions
    # ---------------------------------------------------------
    # Must come before generic lookup / condition handling.
    if (
        condition
        and (
            "find" in q
            or "build" in q
            or "cohort" in q
        )
        and (
            county
            or medication
            or min_age is not None
            or max_age is not None
        )
    ):
        tool = "build_research_cohort"

        args = {
            "condition": condition,
            "county": county,
            "medication": medication,
            "min_age": min_age,
            "max_age": max_age,
        }

    # ---------------------------------------------------------
    # 2. T2DM + ER
    # ---------------------------------------------------------
    # This must happen BEFORE generic diabetes handling.
    elif (
        _contains(q, "er", "emergency", "emergency room", "emergency visit")
        and _contains(q, "diabetes", "t2dm", "type 2")
    ):
        tool = "t2dm_with_er"
        args = {}

    # ---------------------------------------------------------
    # 3. Patient lookup
    # ---------------------------------------------------------
    elif _contains(
        q,
        "lookup",
        "list patients",
        "show patients",
        "patient lookup",
        "patient table",
    ):
        tool = "lookup_patients"

        args = {
            "condition": condition,
            "county": county,
            "limit": 25,
        }

    # ---------------------------------------------------------
    # 4. Data quality
    # ---------------------------------------------------------
    elif _contains(
        q,
        "quality",
        "orphan",
        "future date",
        "data issue",
        "data quality",
    ):
        tool = "get_data_quality"
        args = {}

    # ---------------------------------------------------------
    # 5. County prevalence
    # ---------------------------------------------------------
    elif _contains(
        q,
        "county",
        "prevalence",
        "geographic",
        "fips",
    ):
        tool = "get_county_prevalence"
        args = {}

    # ---------------------------------------------------------
    # 6. Condition trends
    # ---------------------------------------------------------
    elif _contains(
        q,
        "trend",
        "trends",
        "by year",
        "over time",
    ):
        tool = "get_condition_trends"
        args = {}

    # ---------------------------------------------------------
    # 7. Metformin coverage
    # ---------------------------------------------------------
    elif _contains(
        q,
        "metformin",
        "coverage",
    ):
        tool = "metformin_coverage"
        args = {}

    # ---------------------------------------------------------
    # 8. Generic cohort summary
    # ---------------------------------------------------------
    elif condition:
        tool = "get_cohort_summary"
        args = {}

    # ---------------------------------------------------------
    # 9. General overview
    # ---------------------------------------------------------
    elif _contains(
        q,
        "how many",
        "overview",
        "summary",
        "cohort",
        "patients",
    ):
        tool = "get_overview"
        args = {}

    else:
        tool = "get_overview"
        args = {}

    try:
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

    except Exception as exc:
        return {
            "question": question,
            "matched_tool": tool,
            "args": args,
            "message": f"Tool `{tool}` failed: {exc}",
            "examples": EXAMPLES,
            "available_tools": list_tools(),
            "result": None,
            "error": str(exc),
        }