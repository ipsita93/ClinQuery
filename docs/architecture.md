# Architecture

This repo is small on purpose. One story, four layers.

```
CSV (synthetic OMOP tables)
        │
        ▼
DuckDB warehouse  ← optional dbt project in transform/
        │
        ▼
src/catalog.py     named queries (the contract)
        │
        ├────────── FastAPI  /api/*  +  Ask the data box
        └────────── MCP server tools (same functions)
```

## Why DuckDB instead of Snowflake in the default demo

Labs will often ask about Snowflake. The default path uses DuckDB so anyone can clone
the repo with no account, no credit card, and no PHI. The dbt project has a Snowflake
target in `transform/profiles.yml.example`. The mart SQL is ordinary warehouse SQL.

## What “good data management” looks like here

1. **CDM-shaped raw tables** — person, visit_occurrence, condition_occurrence, drug_exposure, concept, location.
2. **Staging views** — types and dates cleaned once.
3. **Marts** — person-grain cohort, yearly trends, county prevalence, quality checks.
4. **Tests** — unique/not-null on `person_id`, accepted 0/1 flags (dbt `schema.yml`).
5. **One query catalog** — the UI does not invent SQL; it calls the same tools MCP exposes.

## Ask the data

`src/nlp.py` is a keyword router, not a hosted LLM. That is a feature for this demo:
it always works offline, the mapping is auditable, and you can explain why a research
group would still put a human-reviewed metric layer in front of free-text SQL.

## MCP

`.mcp.json` starts `src/mcp_server.py`. Tools:

- `ask_data`
- `get_overview`
- `get_cohort_summary`
- `get_condition_trends`
- `get_county_prevalence`
- `get_data_quality`
- `lookup_patients`
- `t2dm_with_er`
- `metformin_coverage`

In Cursor: Settings → MCP → add that config (or open this folder so project MCP loads).
