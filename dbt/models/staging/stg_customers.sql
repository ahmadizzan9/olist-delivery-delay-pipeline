SELECT
    customer_id, 
    customer_city, 
    customer_state
FROM {{ source('raw', 'raw_customers') }}