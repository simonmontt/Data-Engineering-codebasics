USE Voltkart;
GO

SET STATISTICS IO, TIME ON;
GO

WITH orders_2024 AS (
    SELECT
        o.customer_id,
        COUNT(*) AS orders_2024
    FROM dbo.fact_orders AS o
    WHERE o.order_date >= '2024-01-01'
      AND o.order_date <  '2025-01-01'
    GROUP BY
        o.customer_id
),
customer_lifetime_value AS (
    SELECT
        o.customer_id,
        SUM(oi.line_amount) AS lifetime_value
    FROM dbo.fact_orders AS o
    INNER JOIN dbo.fact_order_items AS oi
        ON o.order_id = oi.order_id
    GROUP BY
        o.customer_id
)
SELECT
    o24.customer_id,
    o24.orders_2024,
    clv.lifetime_value
FROM orders_2024 AS o24
LEFT JOIN customer_lifetime_value AS clv
    ON o24.customer_id = clv.customer_id
ORDER BY
    o24.customer_id;

SET STATISTICS IO, TIME OFF;
GO