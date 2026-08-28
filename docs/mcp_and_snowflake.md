# MCP, dbt, and optional Snowflake

## MCP (this repo)

Project config: `.mcp.json`. The server is `src/mcp_server.py` (JSON-RPC on stdio).

After the warehouse exists, an MCP client can call `ask_data` or any named tool in `src/catalog.py`.

The dashboard **Ask the data** box posts to `/api/ask`, which uses `src.nlp.route` → `src.catalog.run_tool`. MCP `ask_data` uses that same route.

## dbt (optional)

The Python builder (`scripts/build_warehouse.py`) is enough to run the app.

If you want the same marts via dbt:

```bash
pip install dbt-duckdb
cd transform
cp profiles.yml.example ~/.dbt/profiles.yml   # or set DBT_PROFILES_DIR
dbt debug --profiles-dir .
dbt build --profiles-dir .
```

`raw_dir` is set in `dbt_project.yml` to `../data/raw`.

## Snowflake (optional)

1. Load the CSVs into a Snowflake database (SnowSQL `PUT`/`COPY`, or an external stage).
2. Point `transform/profiles.yml` at the `snowflake` output (env vars only — see `.env.example`).
3. Replace `read_csv_auto(...)` in staging models with `{{ source('omop_raw', 'person') }}` after you create those tables in Snowflake.
4. `dbt build --target snowflake`

Do not commit passwords. The demo does not require Snowflake.
