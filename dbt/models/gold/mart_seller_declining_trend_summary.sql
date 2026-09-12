WITH months AS (
    SELECT
        seller_id,
        period as current_period,
        total_orders,
        late_rate,
        LAG(period, 1) OVER (PARTITION BY seller_id ORDER BY period) AS period_1m_ago,
        LAG(total_orders, 1) OVER (PARTITION BY seller_id ORDER BY period) AS total_orders_1m_ago,
        LAG(late_rate, 1) OVER (PARTITION BY seller_id ORDER BY period) AS late_rate_1m_ago,
        LAG(period, 2) OVER (PARTITION BY seller_id ORDER BY period) AS period_2m_ago,
        LAG(total_orders, 2) OVER (PARTITION BY seller_id ORDER BY period) AS total_orders_2m_ago,
        LAG(late_rate, 2) OVER (PARTITION BY seller_id ORDER BY period) AS late_rate_2m_ago
    FROM {{ ref('mart_seller_monthly_performance') }}
),
flagged AS (
    SELECT *
    FROM months
    WHERE late_rate_1m_ago IS NOT NULL
      AND late_rate_2m_ago IS NOT NULL
      AND late_rate_1m_ago > 0 
      AND late_rate_2m_ago > 0
      AND AGE (current_period, period_1m_ago) = INTERVAL '1 month'
      AND AGE (period_1m_ago, period_2m_ago) = INTERVAL '1 month'
      AND late_rate > late_rate_1m_ago
      AND late_rate_1m_ago > late_rate_2m_ago
      AND total_orders >= 10
      AND total_orders_1m_ago >= 10
      AND total_orders_2m_ago >= 10
)
SELECT
    date_trunc('quarter', current_period)::date AS quarter,
    COUNT(DISTINCT seller_id) AS total_sellers_declining
FROM flagged
GROUP BY 1
ORDER BY 1