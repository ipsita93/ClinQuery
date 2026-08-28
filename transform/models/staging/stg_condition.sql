select
    condition_occurrence_id,
    person_id,
    condition_concept_id,
    condition_start_date::date as condition_start_date,
    visit_occurrence_id
from read_csv_auto('{{ var("raw_dir") }}/condition_occurrence.csv', header=true)
