SELECT c.id, c.name, AVG(order_totals.order_total) as average_order_value
FROM customers c
         JOIN orders o
              on c.id = o.customer_id
         JOIN (SELECT order_id, SUM(total_price) AS order_total FROM order_items GROUP BY order_id) order_totals
              ON o.id = order_totals.order_id
GROUP BY c.id, c.name
ORDER BY average_order_value DESC;