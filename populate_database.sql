-- First, drop tables if they exist
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- Create tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    registration_date DATE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    sale_date DATE,
    quantity INTEGER,
    total_amount DECIMAL(10, 2)
);

-- Populate Products with a wider range
INSERT INTO products (name, category, price) VALUES
    -- Electronics
    ('Laptop Pro X1', 'Electronics', 1299.99),
    ('Smartphone Galaxy 22', 'Electronics', 899.99),
    ('Tablet Air', 'Electronics', 599.99),
    ('Wireless Earbuds', 'Electronics', 129.99),
    ('Smart Watch Series 5', 'Electronics', 299.99),
    
    -- Furniture
    ('Ergonomic Office Chair', 'Furniture', 249.99),
    ('Standing Desk', 'Furniture', 399.99),
    ('Filing Cabinet', 'Furniture', 159.99),
    ('Bookshelf Deluxe', 'Furniture', 189.99),
    ('Desk Lamp LED', 'Furniture', 49.99),
    
    -- Appliances
    ('Coffee Maker Pro', 'Appliances', 89.99),
    ('Microwave Oven', 'Appliances', 159.99),
    ('Air Purifier', 'Appliances', 199.99),
    ('Water Dispenser', 'Appliances', 129.99),
    ('Blender Professional', 'Appliances', 79.99);

-- Generate 100 customers with realistic data (past year)
INSERT INTO customers (name, email, registration_date)
SELECT 
    'Customer ' || id,
    'customer' || id || '@example.com',
    CURRENT_DATE - (random() * 365)::integer * INTERVAL '1 day'
FROM generate_series(1, 100) as id;

-- Generate sales data for the past year with CURRENT dates
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '12 months',
        CURRENT_DATE,
        '1 day'
    ) AS sale_date
)
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount)
SELECT
    sales_data.customer_id,
    sales_data.product_id,
    sales_data.sale_date,
    sales_data.quantity,
    p.price * sales_data.quantity as total_amount
FROM (
    SELECT 
        1 + floor(random() * 100)::integer as customer_id,
        1 + floor(random() * 15)::integer as product_id,
        sale_date,
        1 + floor(random() * 5)::integer as quantity
    FROM date_series
    CROSS JOIN generate_series(1, 2 + floor(random() * 3)::integer)
) as sales_data
JOIN products p ON p.product_id = sales_data.product_id;

-- Add holiday season sales (using current year)
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount)
SELECT
    holiday_sales.customer_id,
    holiday_sales.product_id,
    holiday_sales.sale_date,
    holiday_sales.quantity,
    p.price * holiday_sales.quantity as total_amount
FROM (
    SELECT 
        1 + floor(random() * 100)::integer as customer_id,
        1 + floor(random() * 15)::integer as product_id,
        sale_date,
        2 + floor(random() * 4)::integer as quantity
    FROM (
        SELECT generate_series(
            CURRENT_DATE - INTERVAL '2 months',
            CURRENT_DATE - INTERVAL '15 days',
            '1 day'
        ) AS sale_date
    ) dates
    CROSS JOIN generate_series(1, 3 + floor(random() * 3)::integer)
) as holiday_sales
JOIN products p ON p.product_id = holiday_sales.product_id;

-- Add specific high-value transactions
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount)
SELECT 
    h.customer_id,
    h.product_id,
    CURRENT_DATE - (random() * 90)::integer * INTERVAL '1 day',
    h.quantity,
    p.price * h.quantity as total_amount
FROM (
    VALUES 
        (1, 1, 3),  -- 3 Laptop Pro X1
        (2, 2, 5),  -- 5 Smartphones
        (3, 7, 2),  -- 2 Standing Desks
        (4, 1, 2),  -- 2 Laptop Pro X1
        (5, 3, 4)   -- 4 Tablets
) AS h(customer_id, product_id, quantity)
JOIN products p ON p.product_id = h.product_id;

-- Add customer preference patterns (electronics)
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount)
SELECT 
    e.customer_id,
    e.product_id,
    CURRENT_DATE - (random() * 180)::integer * INTERVAL '1 day',
    e.quantity,
    p.price * e.quantity as total_amount
FROM (
    SELECT 
        generate_series(1, 10) as customer_id,
        generate_series(1, 5) as product_id,
        1 + floor(random() * 3)::integer as quantity
) as e
JOIN products p ON p.product_id = e.product_id;

-- Add customer preference patterns (furniture)
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount)
SELECT 
    f.customer_id + 10,
    f.product_id,
    CURRENT_DATE - (random() * 180)::integer * INTERVAL '1 day',
    f.quantity,
    p.price * f.quantity as total_amount
FROM (
    SELECT 
        generate_series(1, 10) as customer_id,
        generate_series(6, 10) as product_id,
        1 + floor(random() * 3)::integer as quantity
) as f
JOIN products p ON p.product_id = f.product_id;

-- Add recent customers with immediate purchases
WITH recent_customers AS (
    INSERT INTO customers (name, email, registration_date)
    SELECT 
        'New Customer ' || id,
        'new.customer' || id || '@example.com',
        CURRENT_DATE - (random() * 30)::integer * INTERVAL '1 day'
    FROM generate_series(101, 120) as id
    RETURNING customer_id, registration_date
)
INSERT INTO sales (customer_id, product_id, sale_date, quantity, total_amount)
SELECT 
    rc.customer_id,
    p.product_id,
    rc.registration_date + (random() * 3)::integer * INTERVAL '1 day',
    pd.quantity,
    p.price * pd.quantity as total_amount
FROM recent_customers rc
CROSS JOIN (
    SELECT 
        product_id,
        1 + floor(random() * 3)::integer as quantity
    FROM products 
    WHERE product_id = 1 + floor(random() * 15)::integer
) as pd
JOIN products p ON p.product_id = pd.product_id;

-- Check products
SELECT * FROM products;

-- Check customers
SELECT COUNT(*) as total_customers FROM customers;

-- Check sales
SELECT COUNT(*) as total_sales FROM sales;

-- Quick summary of sales by category
SELECT 
    p.category,
    COUNT(*) as number_of_sales,
    SUM(s.total_amount) as total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.category; 