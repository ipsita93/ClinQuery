select
    drug_exposure_id,
    person_id,
    drug_concept_id,
    drug_exposure_start_date::date as drug_exposure_start_date,
    days_supply
from read_csv_auto('{{ var("raw_dir") }}/drug_exposure.csv', header=true)
