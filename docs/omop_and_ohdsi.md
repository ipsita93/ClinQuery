# OMOP / OHDSI in this project

[OMOP CDM](https://ohdsi.github.io/CommonDataModel/) (Observational Medical Outcomes Partnership Common Data Model) is the table layout many U.S. academic medical centers use so EHR extracts can be compared across sites. [OHDSI](https://www.ohdsi.org/) is the community that maintains the CDM, vocabularies, and tools such as ATLAS.

Johns Hopkins, UCSF, Stanford, and many CTSA hubs participate in OHDSI-style networks. A data manager in those groups is often the person who:

- maps local EHR codes to standard concepts
- keeps person / visit / condition / drug grain honest
- runs quality checks before a PI pulls a cohort
- publishes a mart that analysts can trust

## What this sample includes

| Table | Grain | Role |
| --- | --- | --- |
| `person` | one row per patient | Demographics + `location_id` |
| `visit_occurrence` | one row per visit | Outpatient / inpatient / ER |
| `condition_occurrence` | one row per recorded condition | Linked to visit when present |
| `drug_exposure` | one row per drug start | Metformin, lisinopril |
| `concept` | vocabulary lookup | Names for concept_ids |
| `location` | county | FIPS for public-health rollups |

Concept IDs are well-known example standard concepts (for example Type 2 diabetes mellitus `201826`). This is **not** a licensed Athena vocabulary dump.

## What this sample is not

- Not a full CDM (no procedure, measurement, death, payer, or care site).
- Not real EHR data. Synthetic, public-safe, fine to put on GitHub.
- Not a replacement for Data Quality Dashboard (OHDSI DQD). `mart_data_quality` is a teaching subset: orphan keys and future dates.

## Talking to research groups

If a PI says “we are on OMOP,” you can walk them from raw CDM tables → cohort mart → county prevalence → quality appendix. That is the same conversation whether the warehouse is Snowflake, BigQuery, or a local DuckDB file.
