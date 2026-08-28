select 'orphan_condition_person_id' as check_name,
       'condition_occurrence.person_id has no matching person' as description,
       count(*) as issue_count
from {{ ref('stg_condition') }} c
left join {{ ref('stg_person') }} p on c.person_id = p.person_id
where p.person_id is null

union all

select 'future_visit_dates',
       'visit_start_date is after 2026-08-01',
       count(*)
from {{ ref('stg_visit') }}
where visit_start_date > date '2026-08-01'

union all

select 'missing_gender',
       'person.gender_concept_id is null',
       count(*)
from {{ ref('stg_person') }}
where gender_concept_id is null

union all

select 'person_without_visit',
       'person has no visit_occurrence',
       count(*)
from {{ ref('stg_person') }} p
left join {{ ref('stg_visit') }} v on p.person_id = v.person_id
where v.visit_occurrence_id is null
