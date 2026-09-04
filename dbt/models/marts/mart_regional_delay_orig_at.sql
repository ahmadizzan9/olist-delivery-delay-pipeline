SELECT
    seller_state,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN is_late THEN order_id END) AS late_orders,
    COUNT(DISTINCT CASE WHEN NOT is_late THEN order_id END) AS on_time_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN is_late THEN order_id END)::numeric
        / COUNT(DISTINCT order_id) * 100, 2) AS late_rate_pct,
    CASE 
        WHEN COUNT(DISTINCT order_id) < 100 THEN 'Low sample' ELSE 'Reliable' END AS sample_flag
FROM 
    {{ ref('fact_orders') }}
    JOIN {{ ref('dim_sellers') }} USING (seller_id)
GROUP BY 1
ORDER BY 
	CASE WHEN COUNT(DISTINCT order_id) < 100 THEN 1 ELSE 0 END,
    late_rate_pct DESC