SELECT p.id, p.name
FROM products p
         LEFT JOIN order_items oi
                   ON p.id = oi.product_id
WHERE oi.product_id is NULL;