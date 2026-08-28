select
    visit_occurrence_id,
    person_id,
    visit_concept_id,
    visit_start_date::date as visit_start_date,
    visit_end_date::date as visit_end_date
from read_csv_auto('{{ var("raw_dir") }}/visit_occurrence.csv', header=true)
