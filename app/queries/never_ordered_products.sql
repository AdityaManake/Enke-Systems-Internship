SELECT p.id, p.name, COUNT(p.id) as product_quantity
FROM products p
         INNER JOIN order_items oi
                    ON p.id = oi.product_id
GROUP BY p.id, p.name
having COUNT(oi.product_id) = 0;