-- ============================================================
-- NL2Insight — Ground Truth SQL Queries
-- Dataset: Olist Brazilian E-Commerce
-- These are the "correct answers" we'll test our AI agent against
-- ============================================================


-- ─── REVENUE QUERIES ────────────────────────────────────────

-- Q1: Total revenue across all orders
-- Business question: "What is our total revenue?"
SELECT ROUND(SUM(payment_value), 2) AS total_revenue
FROM order_payments;


-- Q2: Monthly revenue trend
-- Business question: "Show me revenue by month"
SELECT 
    STRFTIME('%Y-%m', order_purchase_timestamp) AS month,
    ROUND(SUM(op.payment_value), 2) AS monthly_revenue
FROM orders o
JOIN order_payments op ON o.order_id = op.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;


-- Q3: Top 10 revenue-generating product categories
-- Business question: "Which product categories make the most money?"
SELECT 
    ct.product_category_name_english AS category,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;


-- ─── ORDER QUERIES ──────────────────────────────────────────

-- Q4: Order status breakdown
-- Business question: "What is the breakdown of order statuses?"
SELECT 
    order_status,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;


-- Q5: Average order value
-- Business question: "What is our average order value?"
SELECT ROUND(AVG(payment_value), 2) AS avg_order_value
FROM order_payments;


-- Q6: Orders per month
-- Business question: "How many orders do we get per month?"
SELECT 
    STRFTIME('%Y-%m', order_purchase_timestamp) AS month,
    COUNT(*) AS total_orders
FROM orders
GROUP BY month
ORDER BY month;


-- ─── CUSTOMER QUERIES ───────────────────────────────────────

-- Q7: Top 10 cities by number of customers
-- Business question: "Which cities have the most customers?"
SELECT 
    customer_city,
    customer_state,
    COUNT(*) AS total_customers
FROM customers
GROUP BY customer_city, customer_state
ORDER BY total_customers DESC
LIMIT 10;


-- Q8: Top 10 states by revenue
-- Business question: "Which states generate the most revenue?"
SELECT 
    c.customer_state,
    ROUND(SUM(op.payment_value), 2) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments op ON o.order_id = op.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;


-- ─── SELLER QUERIES ─────────────────────────────────────────

-- Q9: Top 10 sellers by revenue
-- Business question: "Who are our top performing sellers?"
SELECT 
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY oi.seller_id
ORDER BY total_revenue DESC
LIMIT 10;


-- ─── DELIVERY & LOGISTICS QUERIES ───────────────────────────

-- Q10: Average delivery time in days
-- Business question: "What is our average delivery time?"
SELECT 
    ROUND(AVG(JULIANDAY(order_delivered_customer_date) 
              - JULIANDAY(order_purchase_timestamp)), 1) AS avg_delivery_days
FROM orders
WHERE order_delivered_customer_date IS NOT NULL;


-- Q11: Late deliveries — orders delivered after estimated date
-- Business question: "How many orders were delivered late?"
SELECT 
    COUNT(*) AS late_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders 
                               WHERE order_delivered_customer_date IS NOT NULL), 2) AS late_pct
FROM orders
WHERE order_delivered_customer_date > order_estimated_delivery_date
AND order_delivered_customer_date IS NOT NULL;


-- ─── REVIEW & SATISFACTION QUERIES ──────────────────────────

-- Q12: Average review score
-- Business question: "What is our average customer rating?"
SELECT ROUND(AVG(review_score), 2) AS avg_review_score
FROM order_reviews;


-- Q13: Review score distribution
-- Business question: "How are our review scores distributed?"
SELECT 
    review_score,
    COUNT(*) AS total_reviews,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM order_reviews), 2) AS percentage
FROM order_reviews
GROUP BY review_score
ORDER BY review_score DESC;


-- Q14: Average review score by product category
-- Business question: "Which product categories have the best ratings?"
SELECT 
    ct.product_category_name_english AS category,
    ROUND(AVG(r.review_score), 2) AS avg_rating,
    COUNT(*) AS total_reviews
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY category
HAVING total_reviews > 100
ORDER BY avg_rating DESC
LIMIT 10;


-- ─── PAYMENT QUERIES ────────────────────────────────────────

-- Q15: Payment method breakdown
-- Business question: "What payment methods do customers prefer?"
SELECT 
    payment_type,
    COUNT(*) AS total_transactions,
    ROUND(SUM(payment_value), 2) AS total_value,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM order_payments), 2) AS percentage
FROM order_payments
GROUP BY payment_type
ORDER BY total_transactions DESC;


-- Q16: Average installments for credit card payments
-- Business question: "How many installments do customers use on average?"
SELECT 
    ROUND(AVG(payment_installments), 1) AS avg_installments,
    MAX(payment_installments) AS max_installments
FROM order_payments
WHERE payment_type = 'credit_card';