{{ config(materialized='table') }}

select
    md5(keyword) as keyword_id,
    keyword,
    case keyword
        when 'personal loans'    then 'consumer lending'
        when 'installment loans' then 'consumer lending'
        when 'payday loans'      then 'short-term credit'
        when 'cash advance'      then 'short-term credit'
        when 'credit cards'      then 'revolving credit'
        else 'other'
    end as category
from (
    select distinct keyword
    from {{ ref('stg_google_trends_raw') }}
)
