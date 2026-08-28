#!/usr/bin/env python3
"""Create a small, public-safe OMOP-style sample for this showcase.

The files look like a slice of the OHDSI OMOP Common Data Model (person,
visit, condition, drug, location, concept). They are **synthetic**: no real
patients, no PHI. County names are real U.S. counties so the public-health
story is easy to explain in interviews.

Run from the repo root:

    python scripts/generate_omop_sample.py
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Well-known OMOP concept ids (Athena / OHDSI vocabularies) used as labels.
GENDER = {8507: "MALE", 8532: "FEMALE"}
RACE = {8527: "White", 8516: "Black or African American", 8515: "Asian", 0: "Unknown"}
ETHNICITY = {38003563: "Hispanic or Latino", 38003564: "Not Hispanic or Latino"}

CONDITIONS = [
    (201826, "Type 2 diabetes mellitus", "Condition", "SNOMED", "44054006"),
    (316866, "Essential hypertension", "Condition", "SNOMED", "59621000"),
    (433736, "Obesity", "Condition", "SNOMED", "414916001"),
    (46271022, "Chronic kidney disease", "Condition", "SNOMED", "709044004"),
    (4140453, "Influenza", "Condition", "SNOMED", "6142004"),
    (31967, "Nausea", "Condition", "SNOMED", "422587007"),
]

DRUGS = [
    (1503297, "metformin", "Drug", "RxNorm", "6809"),
    (1308216, "lisinopril", "Drug", "RxNorm", "29046"),
    (1112807, "aspirin", "Drug", "RxNorm", "1191"),
]

VISIT_TYPES = [
    (9202, "Outpatient Visit"),
    (9201, "Inpatient Visit"),
    (9203, "Emergency Room Visit"),
]

# Counties chosen so the map of "where research groups sit" is obvious.
LOCATIONS = [
    (1, "Baltimore", "MD", "Baltimore City", "21205", "24510"),
    (2, "San Francisco", "CA", "San Francisco", "94143", "06075"),
    (3, "Stanford", "CA", "Santa Clara", "94305", "06085"),
    (4, "Oakland", "CA", "Alameda", "94609", "06001"),
    (5, "Rockville", "MD", "Montgomery", "20850", "24031"),
    (6, "Los Angeles", "CA", "Los Angeles", "90095", "06037"),
]


def _write(name: str, fieldnames: list[str], rows: list[dict]) -> None:
    path = RAW / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    start = date(2022, 1, 1)
    end = date(2025, 12, 31)
    span = (end - start).days

    concept_rows = []
    for cid, name in GENDER.items():
        concept_rows.append(
            {
                "concept_id": cid,
                "concept_name": name,
                "domain_id": "Gender",
                "vocabulary_id": "Gender",
                "concept_code": str(cid),
                "standard_concept": "S",
            }
        )
    for cid, name in RACE.items():
        concept_rows.append(
            {
                "concept_id": cid,
                "concept_name": name,
                "domain_id": "Race",
                "vocabulary_id": "Race",
                "concept_code": str(cid),
                "standard_concept": "S" if cid else "",
            }
        )
    for cid, name in ETHNICITY.items():
        concept_rows.append(
            {
                "concept_id": cid,
                "concept_name": name,
                "domain_id": "Ethnicity",
                "vocabulary_id": "Ethnicity",
                "concept_code": str(cid),
                "standard_concept": "S",
            }
        )
    for cid, name, domain, vocab, code in CONDITIONS + DRUGS:
        concept_rows.append(
            {
                "concept_id": cid,
                "concept_name": name,
                "domain_id": domain,
                "vocabulary_id": vocab,
                "concept_code": code,
                "standard_concept": "S",
            }
        )
    for cid, name in VISIT_TYPES:
        concept_rows.append(
            {
                "concept_id": cid,
                "concept_name": name,
                "domain_id": "Visit",
                "vocabulary_id": "Visit",
                "concept_code": str(cid),
                "standard_concept": "S",
            }
        )

    location_rows = [
        {
            "location_id": loc_id,
            "city": city,
            "state": state,
            "county": county,
            "zip": zip_code,
            "location_source_value": fips,
        }
        for loc_id, city, state, county, zip_code, fips in LOCATIONS
    ]

    n_people = 420
    person_rows = []
    for person_id in range(1, n_people + 1):
        gender = rng.choice(list(GENDER))
        race = rng.choices(list(RACE), weights=[58, 22, 14, 6], k=1)[0]
        ethnicity = rng.choices(list(ETHNICITY), weights=[18, 82], k=1)[0]
        location_id = rng.choices([1, 2, 3, 4, 5, 6], weights=[18, 18, 16, 14, 14, 20], k=1)[0]
        year_of_birth = rng.randint(1942, 2002)
        person_rows.append(
            {
                "person_id": person_id,
                "gender_concept_id": gender,
                "year_of_birth": year_of_birth,
                "race_concept_id": race,
                "ethnicity_concept_id": ethnicity,
                "location_id": location_id,
            }
        )

    visit_rows = []
    condition_rows = []
    drug_rows = []
    visit_id = 1
    condition_id = 1
    drug_id = 1

    # Intentional data-quality issues so the quality mart has something to show.
    messy_people = {10, 77, 201}

    for person in person_rows:
        pid = person["person_id"]
        n_visits = rng.randint(1, 6)
        has_t2dm = rng.random() < 0.22
        has_htn = rng.random() < 0.31
        has_obesity = rng.random() < 0.18
        has_ckd = has_t2dm and rng.random() < 0.28

        for _ in range(n_visits):
            visit_concept = rng.choices([9202, 9201, 9203], weights=[70, 12, 18], k=1)[0]
            visit_day = start + timedelta(days=rng.randint(0, span))
            end_day = visit_day + timedelta(days=rng.randint(0, 3 if visit_concept == 9201 else 0))
            if pid in messy_people and rng.random() < 0.4:
                # Future visit date — a classic CDM quality flag.
                visit_day = date(2027, 3, 1)
                end_day = visit_day
            visit_rows.append(
                {
                    "visit_occurrence_id": visit_id,
                    "person_id": pid,
                    "visit_concept_id": visit_concept,
                    "visit_start_date": visit_day.isoformat(),
                    "visit_end_date": end_day.isoformat(),
                }
            )

            problems = []
            if has_t2dm:
                problems.append(201826)
            if has_htn:
                problems.append(316866)
            if has_obesity:
                problems.append(433736)
            if has_ckd:
                problems.append(46271022)
            if rng.random() < 0.12:
                problems.append(4140453)
            if rng.random() < 0.08:
                problems.append(31967)
            if not problems:
                problems.append(rng.choice([201826, 316866, 433736, 4140453]))

            for concept_id in set(problems):
                condition_rows.append(
                    {
                        "condition_occurrence_id": condition_id,
                        "person_id": pid if pid not in messy_people or rng.random() > 0.15 else 99999,
                        "condition_concept_id": concept_id,
                        "condition_start_date": visit_day.isoformat(),
                        "visit_occurrence_id": visit_id,
                    }
                )
                condition_id += 1

                if concept_id == 201826 and rng.random() < 0.75:
                    drug_rows.append(
                        {
                            "drug_exposure_id": drug_id,
                            "person_id": pid,
                            "drug_concept_id": 1503297,
                            "drug_exposure_start_date": visit_day.isoformat(),
                            "days_supply": rng.choice([30, 60, 90]),
                        }
                    )
                    drug_id += 1
                if concept_id == 316866 and rng.random() < 0.7:
                    drug_rows.append(
                        {
                            "drug_exposure_id": drug_id,
                            "person_id": pid,
                            "drug_concept_id": 1308216,
                            "drug_exposure_start_date": visit_day.isoformat(),
                            "days_supply": rng.choice([30, 90]),
                        }
                    )
                    drug_id += 1

            visit_id += 1

    print("Generating synthetic OMOP CSVs…")
    _write(
        "concept.csv",
        ["concept_id", "concept_name", "domain_id", "vocabulary_id", "concept_code", "standard_concept"],
        concept_rows,
    )
    _write(
        "location.csv",
        ["location_id", "city", "state", "county", "zip", "location_source_value"],
        location_rows,
    )
    _write(
        "person.csv",
        [
            "person_id",
            "gender_concept_id",
            "year_of_birth",
            "race_concept_id",
            "ethnicity_concept_id",
            "location_id",
        ],
        person_rows,
    )
    _write(
        "visit_occurrence.csv",
        ["visit_occurrence_id", "person_id", "visit_concept_id", "visit_start_date", "visit_end_date"],
        visit_rows,
    )
    _write(
        "condition_occurrence.csv",
        [
            "condition_occurrence_id",
            "person_id",
            "condition_concept_id",
            "condition_start_date",
            "visit_occurrence_id",
        ],
        condition_rows,
    )
    _write(
        "drug_exposure.csv",
        ["drug_exposure_id", "person_id", "drug_concept_id", "drug_exposure_start_date", "days_supply"],
        drug_rows,
    )
    print("Done. These files are synthetic and safe to publish.")


if __name__ == "__main__":
    main()
