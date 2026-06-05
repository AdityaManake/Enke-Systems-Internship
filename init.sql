CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price NUMERIC(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  product_id INT NOT NULL REFERENCES products(id),
  quantity INT NOT NULL DEFAULT 1,
  total_price NUMERIC(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (email, name) VALUES
('alice@example.com', 'Alice'),
('bob@example.com', 'Bob');

INSERT INTO products (name, price) VALUES
('Keyboard', 49.99),
('Mouse', 19.99),
('Monitor', 199.99);

INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES
(1, 1, 2, 99.98),
(1, 3, 1, 199.99),
(2, 2, 3, 59.97);