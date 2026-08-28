# Sample findings (synthetic OMOP mart)

_Generated 2026-08-28. Not real patients. Not for clinical use._

## Cohort snapshot

- **420** synthetic patients, **1449** visits, **266** ER visits.
- Type 2 diabetes: **42.1%**. Hypertension: **47.9%**. Obesity: **35.7%**.
- Among T2DM patients, **47.5%** had at least one ER visit.
- Metformin recorded for **88.7%** of T2DM patients.

## County prevalence

| County | State | Patients | T2DM % | HTN % | Mean ER visits |
| --- | --- | --- | --- | --- | --- |
| Los Angeles | CA | 81 | 40.7 | 40.7 | 0.54 |
| San Francisco | CA | 77 | 48.1 | 48.1 | 0.61 |
| Baltimore City | MD | 76 | 39.5 | 51.3 | 0.62 |
| Alameda | CA | 66 | 42.4 | 51.5 | 0.79 |
| Santa Clara | CA | 63 | 39.7 | 49.2 | 0.71 |
| Montgomery | MD | 57 | 42.1 | 47.4 | 0.54 |

## Data quality (intentional flags in the sample)

| Check | Description | Issues |
| --- | --- | --- |
| `orphan_condition_person_id` | condition_occurrence.person_id has no matching person | 1 |
| `future_visit_dates` | visit_start_date is after 2026-08-01 | 0 |
| `missing_gender` | person.gender_concept_id is null | 0 |
| `person_without_visit` | person has no visit_occurrence | 0 |

## How to talk about this in an interview

This is the kind of mart a data manager would hand a methods PI: person-grain flags,
a geographic rollup for public health, and a short quality appendix before anyone
fits a model. The dashboard and MCP `ask_data` tool read these same tables.
