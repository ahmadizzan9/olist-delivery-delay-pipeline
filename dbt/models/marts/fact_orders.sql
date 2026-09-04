SELECT
    order_id,
    customer_id,
    product_id,
    seller_id,
    order_purchase_timestamp,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    is_late,
    delay_days,
    review_score,
    price,
    freight_value
from
    {{ ref('stg_orders') }}
    join {{ ref('stg_order_items') }} using (order_id)
    left join {{ ref('stg_reviews') }} using (order_id)