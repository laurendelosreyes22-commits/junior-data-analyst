{{ config(materialized='table') }}

select
    md5(region) as region_id,
    region
from (
    select distinct region
    from {{ ref('stg_google_trends_raw') }}
)
