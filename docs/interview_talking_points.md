# Interview talking points

Use this repo as a **portfolio artifact**, not as a claim that you ran a production CDM.

## One-minute pitch

> I built a small OMOP-style data mart with synthetic U.S. patients: staging, person-grain flags, county prevalence, and data-quality checks. A dashboard and an MCP server call the same query catalog, so “ask the data” cannot drift from the documented metrics.

## What a data manager at JHU / UCSF / Stanford actually does

Tie each piece of the repo to the job, not to the framework name.

| Job you want them to picture | Where it is in the repo |
| --- | --- |
| Keep a CDM extract understandable | `docs/omop_and_ohdsi.md`, raw CSVs |
| Publish analysis-ready tables | `mart_patient_cohort`, `mart_county_prevalence` |
| Catch bad joins before a paper | `mart_data_quality`, dbt tests in `transform/models/schema.yml` |
| Let PIs explore without writing unsafe SQL | `src/catalog.py` + Ask the data + MCP |
| Run locally first, warehouse later | DuckDB default, Snowflake profile example |

## Questions you can invite

- “How would you add measurement (A1c) without breaking person grain?”
- “Why is county prevalence a different grain from the cohort mart?”
- “Why not let the LLM write arbitrary SQL?”
- “What would you test if this landed in Snowflake with 12 sites?”

## Honesty

Say clearly: synthetic data, subset of OMOP, keyword NLP. That reads as senior. Overclaiming a full OHDSI stack reads as junior.
