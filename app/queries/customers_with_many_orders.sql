SELECT c.id, c.name, COUNT(o.id) AS total_orders
from customers c
         INNER JOIN orders o
                    ON c.id = o.customer_id
GROUP BY c.id, c.name
HAVING COUNT(o.id) > 5;