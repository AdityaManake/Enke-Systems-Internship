SELECT c.id, c.name, AVG(oi.total_price) as average_order__value
FROM customers c
         INNER JOIN orders o
                    on c.id = o.customer_id
         INNER JOIN order_items oi
                    ON o.id = oi.order_id
GROUP BY c.id, c.name
ORDER BY average_order__value ASC;
