INSERT INTO analytics.orders_per_month(month, total_orders)

SELECT
    DATE_TRUNC('month', created_at)::DATE AS month,
    COUNT(*) AS total_orders
FROM orders
WHERE :last_sync IS NULL
   OR created_at > :last_sync
GROUP BY DATE_TRUNC('month', created_at)

ON CONFLICT (month)
DO UPDATE
SET total_orders =
    analytics.orders_per_month.total_orders
    + EXCLUDED.total_orders;