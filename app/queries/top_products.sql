SELECT p.id, p.name, p.price, SUM(oi.order_items)
FROM products p
INNER JOIN
order_items oi
ON p.id = oi.product_id
GROUP BY p.id, p.name, p.price
ORDER BY total_revenue DESC
LIMIT 10;