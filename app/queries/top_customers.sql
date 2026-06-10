SELECT c.id, c.name, SUM(oi.total_price) as total_amount_spend
FROM customers c
INNER JOIN
orders o
ON c.id =o.customer_id
INNER JOIN
order_items oi
ON o.id = oi.order_id
GROUP BY  c.id, c.name
ORDER BY  total_amount_spend DESC
LIMIT 10;
