-- Authors table
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE
);

COMMENT ON COLUMN authors.author_id IS 'Unique identifier for each author';
COMMENT ON COLUMN authors.name IS 'Full name of the author';
COMMENT ON COLUMN authors.birth_date IS 'Date of birth of the author';

-- Books table
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER REFERENCES authors(author_id),
    isbn VARCHAR(13) UNIQUE,
    price DECIMAL(10, 2),
    publication_date DATE
);

COMMENT ON COLUMN books.book_id IS 'Unique identifier for each book';
COMMENT ON COLUMN books.title IS 'Title of the book';
COMMENT ON COLUMN books.author_id IS 'Foreign key referencing the author of the book';
COMMENT ON COLUMN books.isbn IS 'International Standard Book Number (13 digits)';
COMMENT ON COLUMN books.price IS 'Price of the book in decimal format';
COMMENT ON COLUMN books.publication_date IS 'Date when the book was published';

-- Customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    registration_date DATE
);

COMMENT ON COLUMN customers.customer_id IS 'Unique identifier for each customer';
COMMENT ON COLUMN customers.first_name IS 'First name of the customer';
COMMENT ON COLUMN customers.last_name IS 'Last name of the customer';
COMMENT ON COLUMN customers.email IS 'Email address of the customer (unique)';
COMMENT ON COLUMN customers.registration_date IS 'Date when the customer registered';

-- Orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE,
    total_amount DECIMAL(10, 2)
);

COMMENT ON COLUMN orders.order_id IS 'Unique identifier for each order';
COMMENT ON COLUMN orders.customer_id IS 'Foreign key referencing the customer who placed the order';
COMMENT ON COLUMN orders.order_date IS 'Date when the order was placed';
COMMENT ON COLUMN orders.total_amount IS 'Total amount of the order in decimal format';

-- Order Items table
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    book_id INTEGER REFERENCES books(book_id),
    quantity INTEGER,
    price DECIMAL(10, 2)
);

COMMENT ON COLUMN order_items.order_item_id IS 'Unique identifier for each order item';
COMMENT ON COLUMN order_items.order_id IS 'Foreign key referencing the order';
COMMENT ON COLUMN order_items.book_id IS 'Foreign key referencing the book in the order';
COMMENT ON COLUMN order_items.quantity IS 'Quantity of books ordered';
COMMENT ON COLUMN order_items.price IS 'Price of the book at the time of order';

-- Reviews table
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(book_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date DATE
);

COMMENT ON COLUMN reviews.review_id IS 'Unique identifier for each review';
COMMENT ON COLUMN reviews.book_id IS 'Foreign key referencing the book being reviewed';
COMMENT ON COLUMN reviews.customer_id IS 'Foreign key referencing the customer who wrote the review';
COMMENT ON COLUMN reviews.rating IS 'Rating given by the customer (1-5)';
COMMENT ON COLUMN reviews.review_text IS 'Text content of the review';
COMMENT ON COLUMN reviews.review_date IS 'Date when the review was submitted';

-- Insert sample data
INSERT INTO authors (name, birth_date) VALUES
('J.K. Rowling', '1965-07-31'),
('George Orwell', '1903-06-25'),
('Jane Austen', '1775-12-16');

INSERT INTO books (title, author_id, isbn, price, publication_date) VALUES
('Harry Potter and the Philosopher''s Stone', 1, '9780747532743', 19.99, '1997-06-26'),
('1984', 2, '9780451524935', 12.99, '1949-06-08'),
('Pride and Prejudice', 3, '9780141439518', 9.99, '1813-01-28');

INSERT INTO customers (first_name, last_name, email, registration_date) VALUES
('John', 'Doe', 'john.doe@example.com', '2023-01-15'),
('Jane', 'Smith', 'jane.smith@example.com', '2023-02-20'),
('Bob', 'Johnson', 'bob.johnson@example.com', '2023-03-10');

INSERT INTO orders (customer_id, order_date, total_amount) VALUES
(1, '2023-04-01', 19.99),
(2, '2023-04-15', 22.98),
(3, '2023-04-30', 19.99);

INSERT INTO order_items (order_id, book_id, quantity, price) VALUES
(1, 1, 1, 19.99),
(2, 2, 1, 12.99),
(2, 3, 1, 9.99),
(3, 1, 1, 19.99);

INSERT INTO reviews (book_id, customer_id, rating, review_text, review_date) VALUES
(1, 1, 5, 'Amazing book! Couldn''t put it down.', '2023-04-10'),
(2, 2, 4, 'A classic dystopian novel. Thought-provoking.', '2023-04-25'),
(3, 3, 5, 'Jane Austen at her best. Witty and romantic.', '2023-05-05');

-- Create a user for database access
CREATE USER bookstore_user WITH PASSWORD 'userpassword';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bookstore_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bookstore_user;