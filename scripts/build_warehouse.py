#!/usr/bin/env python3
"""Load raw OMOP CSVs into DuckDB and build the analysis marts.

This is the local stand-in for a warehouse + dbt run. The SQL is intentionally
plain so you can point the same logic at Snowflake later (see transform/).

Run from the repo root:

    python scripts/build_warehouse.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import duckdb  # noqa: E402

from src.paths import RAW_DIR, WAREHOUSE_DIR, WAREHOUSE_PATH  # noqa: E402


def build() -> Path:
    if not (RAW_DIR / "person.csv").exists():
        raise SystemExit("Raw CSVs missing. Run: python scripts/generate_omop_sample.py")

    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    if WAREHOUSE_PATH.exists():
        WAREHOUSE_PATH.unlink()

    con = duckdb.connect(str(WAREHOUSE_PATH))
    raw = str(RAW_DIR).replace("\\", "/")

    con.execute(
        f"""
        create table person as select * from read_csv_auto('{raw}/person.csv', header=true);
        create table location as select * from read_csv_auto('{raw}/location.csv', header=true);
        create table concept as select * from read_csv_auto('{raw}/concept.csv', header=true);
        create table visit_occurrence as select * from read_csv_auto('{raw}/visit_occurrence.csv', header=true);
        create table condition_occurrence as select * from read_csv_auto('{raw}/condition_occurrence.csv', header=true);
        create table drug_exposure as select * from read_csv_auto('{raw}/drug_exposure.csv', header=true);
        """
    )

    con.execute(
        """
        create view stg_person as
        select
            person_id,
            gender_concept_id,
            year_of_birth,
            race_concept_id,
            ethnicity_concept_id,
            location_id,
            2026 - year_of_birth as age_years
        from person;

        create view stg_visit as
        select
            visit_occurrence_id,
            person_id,
            visit_concept_id,
            visit_start_date::date as visit_start_date,
            visit_end_date::date as visit_end_date,
            date_diff('day', visit_start_date::date, visit_end_date::date) as los_days
        from visit_occurrence;

        create view stg_condition as
        select
            condition_occurrence_id,
            person_id,
            condition_concept_id,
            condition_start_date::date as condition_start_date,
            visit_occurrence_id
        from condition_occurrence;

        create view stg_drug as
        select
            drug_exposure_id,
            person_id,
            drug_concept_id,
            drug_exposure_start_date::date as drug_exposure_start_date,
            days_supply
        from drug_exposure;
        """
    )

    con.execute(
        """
        create table mart_patient_cohort as
        with visit_stats as (
            select
                person_id,
                count(*) as visit_count,
                sum(case when visit_concept_id = 9203 then 1 else 0 end) as er_visit_count
            from stg_visit
            group by 1
        ),
        condition_flags as (
            select
                person_id,
                max(case when condition_concept_id = 201826 then 1 else 0 end) as has_t2dm,
                max(case when condition_concept_id = 316866 then 1 else 0 end) as has_hypertension,
                max(case when condition_concept_id = 433736 then 1 else 0 end) as has_obesity,
                max(case when condition_concept_id = 46271022 then 1 else 0 end) as has_ckd,
                max(case when condition_concept_id = 4140453 then 1 else 0 end) as has_influenza
            from stg_condition
            group by 1
        ),
        drug_flags as (
            select
                person_id,
                max(case when drug_concept_id = 1503297 then 1 else 0 end) as on_metformin,
                max(case when drug_concept_id = 1308216 then 1 else 0 end) as on_lisinopril
            from stg_drug
            group by 1
        )
        select
            p.person_id,
            p.age_years,
            g.concept_name as gender,
            r.concept_name as race,
            e.concept_name as ethnicity,
            l.city,
            l.state,
            l.county,
            l.location_source_value as fips,
            coalesce(c.has_t2dm, 0) as has_t2dm,
            coalesce(c.has_hypertension, 0) as has_hypertension,
            coalesce(c.has_obesity, 0) as has_obesity,
            coalesce(c.has_ckd, 0) as has_ckd,
            coalesce(c.has_influenza, 0) as has_influenza,
            coalesce(v.visit_count, 0) as visit_count,
            coalesce(v.er_visit_count, 0) as er_visit_count,
            coalesce(d.on_metformin, 0) as on_metformin,
            coalesce(d.on_lisinopril, 0) as on_lisinopril
        from stg_person p
        left join location l on p.location_id = l.location_id
        left join concept g on p.gender_concept_id = g.concept_id
        left join concept r on p.race_concept_id = r.concept_id
        left join concept e on p.ethnicity_concept_id = e.concept_id
        left join condition_flags c on p.person_id = c.person_id
        left join visit_stats v on p.person_id = v.person_id
        left join drug_flags d on p.person_id = d.person_id;

        create table mart_condition_trends as
        select
            year(c.condition_start_date) as year,
            c.condition_concept_id,
            voc.concept_name as condition_name,
            count(*) as condition_events,
            count(distinct c.person_id) as unique_patients
        from stg_condition c
        join concept voc on c.condition_concept_id = voc.concept_id
        where year(c.condition_start_date) between 2022 and 2025
        group by 1,2,3
        order by 1, 4 desc;

        create table mart_county_prevalence as
        select
            county,
            state,
            fips,
            count(*) as patients,
            round(100.0 * avg(has_t2dm), 1) as t2dm_pct,
            round(100.0 * avg(has_hypertension), 1) as htn_pct,
            round(100.0 * avg(has_obesity), 1) as obesity_pct,
            round(100.0 * avg(has_ckd), 1) as ckd_pct,
            round(avg(er_visit_count), 2) as mean_er_visits
        from mart_patient_cohort
        group by 1,2,3
        order by patients desc;

        create table mart_data_quality as
        select 'orphan_condition_person_id' as check_name,
               'condition_occurrence.person_id has no matching person' as description,
               count(*) as issue_count
        from condition_occurrence c
        left join person p on c.person_id = p.person_id
        where p.person_id is null
        union all
        select 'future_visit_dates',
               'visit_start_date is after 2026-08-01',
               count(*)
        from visit_occurrence
        where visit_start_date::date > date '2026-08-01'
        union all
        select 'missing_gender',
               'person.gender_concept_id is null',
               count(*)
        from person
        where gender_concept_id is null
        union all
        select 'person_without_visit',
               'person has no visit_occurrence',
               count(*)
        from person p
        left join visit_occurrence v on p.person_id = v.person_id
        where v.visit_occurrence_id is null;
        """
    )

    con.close()
    print(f"Warehouse ready: {WAREHOUSE_PATH.relative_to(ROOT)}")
    return WAREHOUSE_PATH


if __name__ == "__main__":
    build()
