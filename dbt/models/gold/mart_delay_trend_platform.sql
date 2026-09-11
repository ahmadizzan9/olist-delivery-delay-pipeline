SELECT
    date_trunc('month', order_delivered_customer_date)::date AS period,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN is_late THEN order_id END) AS late_orders,
    ROUND(COUNT(DISTINCT CASE WHEN is_late THEN order_id END)::numeric
        / COUNT(DISTINCT order_id) * 100, 2) AS late_rate_pct
FROM {{ ref('fact_orders') }}
GROUP BY 1
ORDER BY 1

