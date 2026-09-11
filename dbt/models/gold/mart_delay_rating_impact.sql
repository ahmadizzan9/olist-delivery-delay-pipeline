with order_level as (
    select distinct
        order_id,
        delay_days,
        review_score
    from {{ ref('fact_orders') }}
    where review_score is not null
)
select
    case
        when delay_days <= 0  then '0. on-time'
        when delay_days <= 3  then '1. delayed 1-3 days'
        when delay_days <= 7  then '2. delayed 4-7 days'
        when delay_days <= 14 then '3. delayed 8-14 days'
        else '4. delayed >14 days'
    end as delay_bucket,
    count(*) as total_orders,
    avg(review_score) as avg_review_score
from order_level
group by 1
order by delay_bucket