# OMOP public-health data mart (showcase)

A **small, public-safe** project for data-management interviews in U.S. academic medicine and public health (Johns Hopkins, UCSF, Stanford, CTSA / research-informatics groups).

It shows one complete path:

**synthetic OMOP-style tables → DuckDB marts (optional dbt / Snowflake) → named queries → dashboard + MCP “ask the data.”**

No real patients. No API keys. Clone, run, screenshot, put on GitHub.

## What you get

- **OMOP-shaped extract:** `person`, `visit_occurrence`, `condition_occurrence`, `drug_exposure`, `concept`, `location` (U.S. counties including Baltimore City, San Francisco, Santa Clara).
- **Marts:** person-grain chronic-disease cohort, yearly condition trends, county prevalence, data-quality flags.
- **Lightweight frontend:** KPI cards, Chart.js, county/quality tables, patient lookup, and an **Ask the data** box that calls the **same functions** as the MCP tools (`src/catalog.py`).
- **MCP server** for Cursor (or any MCP client).
- **Docs** written for hiring managers, not only engineers.

| Doc | Use |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | How the pieces connect |
| [docs/omop_and_ohdsi.md](docs/omop_and_ohdsi.md) | CDM context for research groups |
| [docs/interview_talking_points.md](docs/interview_talking_points.md) | How to describe this in a screen |
| [docs/mcp_and_snowflake.md](docs/mcp_and_snowflake.md) | Optional dbt + Snowflake |
| [docs/github.md](docs/github.md) | Make the repo public |
| [reports/sample_findings.md](reports/sample_findings.md) | Generated summary tables |

## Run in five minutes

Python 3.9+ (3.12 recommended). From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/generate_omop_sample.py
python scripts/build_warehouse.py
python scripts/write_report.py

python -m src.api
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

Try questions such as:

- How many patients are in the cohort?
- What is hypertension prevalence by county?
- Show data quality issues
- Type 2 diabetes patients with ER visits
- Lookup diabetes patients in San Francisco

## MCP

Project file: `.mcp.json`. Point Cursor MCP at:

```text
command: python
args: ["src/mcp_server.py"]
```

Run `generate` + `build_warehouse` first so DuckDB exists. Tools wrap `src.catalog` (`ask_data`, `get_overview`, `lookup_patients`, …).

## Optional dbt / Snowflake

The app does **not** need dbt. The `transform/` project is the same marts expressed as dbt models (DuckDB default, Snowflake target in `profiles.yml.example`). See [docs/mcp_and_snowflake.md](docs/mcp_and_snowflake.md).

## Publish on GitHub

```bash
chmod +x scripts/publish_github.sh
./scripts/publish_github.sh omop-public-health-showcase
```

Details: [docs/github.md](docs/github.md).

## Design choices (short)

- **Synthetic data** so the repo can be public.
- **Keyword “NLP”** so Ask the data works offline and stays auditable. Swap in an LLM later; keep `catalog.py` as the allowlist.
- **DuckDB first** so reviewers are not blocked on a warehouse account.
- **Quality mart with intentional errors** so you can talk about CDM hygiene, not only pretty charts.

MIT license. OMOP concept *names* are for demonstration; this is not a licensed vocabulary distribution.
