select
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    (order_delivered_customer_date::date > order_estimated_delivery_date::date) as is_late,
    (order_delivered_customer_date::date - order_estimated_delivery_date::date) as delay_days

from {{ source('raw', 'raw_orders') }}

where order_status = 'delivered'
  -- exclude order dengan tanggal kunci yang kosong (null)
  and order_delivered_customer_date is not null
  and order_estimated_delivery_date is not null
  and order_delivered_carrier_date is not null
  -- exclude urutan tanggal yang tidak logis
  and order_purchase_timestamp <= order_approved_at
  and order_approved_at <= order_delivered_carrier_date
  and order_delivered_carrier_date <= order_delivered_customer_date
  -- exclude tanggal yang melebihi batas
  and order_delivered_customer_date < '2018-09-01'::date