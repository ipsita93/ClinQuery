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
from {{ ref('mart_patient_cohort') }}
group by 1, 2, 3
