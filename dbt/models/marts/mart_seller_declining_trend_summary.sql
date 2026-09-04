WITH months AS (
    SELECT
        seller_id,
        period,
        total_orders,
        late_rate,
        LAG(total_orders, 1) OVER (PARTITION BY seller_id ORDER BY period) AS total_orders_1m_ago,
        LAG(late_rate, 1) OVER (PARTITION BY seller_id ORDER BY period) AS late_rate_1m_ago,
        LAG(total_orders, 2) OVER (PARTITION BY seller_id ORDER BY period) AS total_orders_2m_ago,
        LAG(late_rate, 2) OVER (PARTITION BY seller_id ORDER BY period) AS late_rate_2m_ago
    FROM {{ ref('mart_seller_monthly_performance') }}
),
flagged AS (
    SELECT *
    FROM months
    WHERE late_rate_1m_ago IS NOT NULL
      AND late_rate_2m_ago IS NOT NULL
      AND late_rate > late_rate_1m_ago
      AND late_rate_1m_ago > late_rate_2m_ago
      AND total_orders >= 10
      AND total_orders_1m_ago >= 10
      AND total_orders_2m_ago >= 10
)
SELECT
    date_trunc('quarter', period)::date AS quarter,
    COUNT(DISTINCT seller_id) AS n_sellers_declining
FROM flagged
GROUP BY 1
ORDER BY 1