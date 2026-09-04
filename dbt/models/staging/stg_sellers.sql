SELECT
    seller_id, 
    seller_city, 
    seller_state
FROM {{ source('raw', 'raw_sellers') }}