SELECT c.id, c.name, MAX(order_totals.order_total) AS most_expensive_order
FROM customers c
         JOIN orders o ON c.id = o.customer_id
         JOIN (SELECT order_id, SUM(total_price) AS order_total FROM order_items GROUP BY order_id) order_totals
              ON o.id = order_totals.order_id
GROUP BY c.id, c.name
ORDER BY most_expensive_order DESC;