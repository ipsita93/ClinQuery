select
    year(c.condition_start_date) as year,
    c.condition_concept_id,
    voc.concept_name as condition_name,
    count(*) as condition_events,
    count(distinct c.person_id) as unique_patients
from {{ ref('stg_condition') }} c
join {{ ref('stg_concept') }} voc on c.condition_concept_id = voc.concept_id
where year(c.condition_start_date) between 2022 and 2025
group by 1, 2, 3
