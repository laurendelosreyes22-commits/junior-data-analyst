{{ config(materialized='table') }}

select
    dk.keyword_id,
    dr.region_id,
    dd.date_id,
    s.interest_value
from {{ ref('stg_google_trends_raw') }}   s
join {{ ref('dim_keyword') }}             dk on s.keyword    = dk.keyword
join {{ ref('dim_region') }}              dr on s.region     = dr.region
join {{ ref('dim_date') }}                dd on s.week_start = dd.week_start
