"""Local dashboard API. All endpoints call src.catalog — same as MCP tools."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.catalog import (  # noqa: E402
    get_condition_trends,
    get_county_prevalence,
    get_data_quality,
    get_overview,
    list_tools,
    lookup_patients,
)
from src.nlp import EXAMPLES, route  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="OMOP Public Health Showcase",
    description="Tiny OMOP-style mart + Ask the data. Synthetic patients only.",
    version="0.1.0",
)


@app.get("/api/overview")
def api_overview():
    return get_overview()


@app.get("/api/trends")
def api_trends():
    return get_condition_trends()


@app.get("/api/counties")
def api_counties():
    return get_county_prevalence()


@app.get("/api/quality")
def api_quality():
    return get_data_quality()


@app.get("/api/lookup")
def api_lookup(
    condition: Optional[str] = None,
    county: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
):
    return lookup_patients(condition=condition, county=county, limit=limit)


@app.get("/api/tools")
def api_tools():
    return list_tools()


@app.get("/api/examples")
def api_examples():
    return EXAMPLES


@app.post("/api/ask")
def api_ask(payload: dict):
    return route(str(payload.get("question") or ""))


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")


def main() -> None:
    import uvicorn

    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
