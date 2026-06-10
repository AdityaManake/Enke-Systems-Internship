SELECT c.id, c.name, MAX(oi.total_price) as most_expensive_order
FROM customers c
         INNER JOIN orders o
                    ON c.id = o.customer_id
         INNER JOIN order_items oi
                    on o.id = oi.order_id
GROUP BY c.id, c.name
ORDER BY most_expensive_order DESC;