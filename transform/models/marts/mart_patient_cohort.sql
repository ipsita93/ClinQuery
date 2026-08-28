with visit_stats as (
    select
        person_id,
        count(*) as visit_count,
        sum(case when visit_concept_id = 9203 then 1 else 0 end) as er_visit_count
    from {{ ref('stg_visit') }}
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
    from {{ ref('stg_condition') }}
    group by 1
),

drug_flags as (
    select
        person_id,
        max(case when drug_concept_id = 1503297 then 1 else 0 end) as on_metformin,
        max(case when drug_concept_id = 1308216 then 1 else 0 end) as on_lisinopril
    from {{ ref('stg_drug') }}
    group by 1
)

select
    p.person_id,
    (2026 - p.year_of_birth) as age_years,
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
from {{ ref('stg_person') }} p
left join {{ ref('stg_location') }} l on p.location_id = l.location_id
left join {{ ref('stg_concept') }} g on p.gender_concept_id = g.concept_id
left join {{ ref('stg_concept') }} r on p.race_concept_id = r.concept_id
left join {{ ref('stg_concept') }} e on p.ethnicity_concept_id = e.concept_id
left join condition_flags c on p.person_id = c.person_id
left join visit_stats v on p.person_id = v.person_id
left join drug_flags d on p.person_id = d.person_id
