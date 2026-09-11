SELECT
    order_id, 
    review_score
FROM {{ source('raw', 'raw_reviews') }}