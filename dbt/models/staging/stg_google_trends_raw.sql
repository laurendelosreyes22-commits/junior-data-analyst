select
    keyword,
    region,
    week_start::date        as week_start,
    interest_value::integer as interest_value,
    loaded_at
from {{ source('raw', 'google_trends_raw') }}
