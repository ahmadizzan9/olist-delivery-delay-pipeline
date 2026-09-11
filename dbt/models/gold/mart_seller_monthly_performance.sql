select
    seller_id,
    date_trunc('month', order_delivered_customer_date)::date as period,
    count(distinct order_id) as total_orders,
    avg(case when is_late then 1.0 else 0 end) as late_rate,
    avg(review_score) as avg_review_score
from {{ ref('fact_orders') }}
group by 1, 2