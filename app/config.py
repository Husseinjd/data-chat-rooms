import os
from dotenv import load_dotenv

load_dotenv()

# Get the OpenAI API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")    


EXAMPLE_QUERIES = [
      {
       
        "description": "Show me all books in the database along with their authors.",
        "query": "SELECT b.title, a.name AS author FROM books b JOIN authors a ON b.author_id = a.author_id;"
      },
      {
       
        "description": "What is the most expensive book in our inventory?",
        "query": "SELECT title, price FROM books ORDER BY price DESC LIMIT 1;"
      },
      {
       
        "description": "How many books has each author written?",
        "query": "SELECT a.name, COUNT(b.book_id) AS book_count FROM authors a LEFT JOIN books b ON a.author_id = b.author_id GROUP BY a.author_id, a.name ORDER BY book_count DESC;"
      },
      {
       
        "description": "Which customers have not made any purchases yet?",
        "query": "SELECT c.first_name, c.last_name, c.email FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;"
      },
      {
       
        "description": "What is our total sales amount across all orders?",
        "query": "SELECT SUM(total_amount) AS total_sales FROM orders;"
      },
      {
       
        "description": "Show me all books with an average rating of 4 or higher.",
        "query": "SELECT b.title, AVG(r.rating) AS avg_rating FROM books b JOIN reviews r ON b.book_id = r.book_id GROUP BY b.book_id, b.title HAVING AVG(r.rating) >= 4 ORDER BY avg_rating DESC;"
      },
      {
       
        "description": "Who is our most popular author based on the number of books sold?",
        "query": "SELECT a.name, SUM(oi.quantity) AS books_sold FROM authors a JOIN books b ON a.author_id = b.author_id JOIN order_items oi ON b.book_id = oi.book_id GROUP BY a.author_id, a.name ORDER BY books_sold DESC LIMIT 1;"
      },
      {
       
        "description": "Show me the 5 most recent orders with customer names and order totals.",
        "query": "SELECT o.order_id, c.first_name, c.last_name, o.order_date, o.total_amount FROM orders o JOIN customers c ON o.customer_id = c.customer_id ORDER BY o.order_date DESC LIMIT 5;"
      },
      {
       
        "description": "Which books have not received any reviews yet?",
        "query": "SELECT b.title FROM books b LEFT JOIN reviews r ON b.book_id = r.book_id WHERE r.review_id IS NULL;"
      },
      {
       
        "description": "What is the average order value in our bookstore?",
        "query": "SELECT AVG(total_amount) AS avg_order_value FROM orders;"
      },
      {
       
        "description": "Who are our top 5 customers based on their total spend?",
        "query": "SELECT c.first_name, c.last_name, SUM(o.total_amount) AS total_spend FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_spend DESC LIMIT 5;"
      },
      {
       
        "description": "Show all books published in 1997.",
        "query": "SELECT title, publication_date FROM books WHERE EXTRACT(YEAR FROM publication_date) = 1997;"
      },
      {
       
        "description": "For each customer, show their name and the date of their most recent order.",
        "query": "SELECT c.first_name, c.last_name, MAX(o.order_date) AS latest_order_date FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.first_name, c.last_name;"
      },
      {
       
        "description": "Show total sales for each month of the current year.",
        "query": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(total_amount) AS monthly_sales FROM orders WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY EXTRACT(MONTH FROM order_date) ORDER BY month;"
      },
      {
       
        "description": "Which books have never been ordered?",
        "query": "SELECT b.title FROM books b LEFT JOIN order_items oi ON b.book_id = oi.book_id WHERE oi.order_item_id IS NULL;"
      }
    ]