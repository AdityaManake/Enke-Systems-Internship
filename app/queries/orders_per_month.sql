SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS total_orders
FROM orders
WHERE :last_sync IS NULL
    OR created_at > :last_sync
GROUP BY month
ORDER BY month;