SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS total_orders
FROM orders
GROUP BY month
ORDER BY month;