{{ config(materialized='table') }}

select
    md5(cast(week_start as varchar)) as date_id,
    week_start,
    month(week_start)   as month,
    year(week_start)    as year,
    quarter(week_start) as quarter
from (
    select distinct week_start
    from {{ ref('stg_google_trends_raw') }}
)
