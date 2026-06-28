USE Voltkart;
GO

WITH product_revenue AS (
    SELECT
        dc.category_id,
        dc.category_name,
        dp.product_id,
        dp.product_name,
        SUM(foi.quantity * foi.unit_price) AS total_revenue
    FROM dbo.fact_order_items AS foi
    INNER JOIN dbo.fact_orders AS fo
        ON foi.order_id = fo.order_id
    INNER JOIN dbo.dim_product AS dp
        ON foi.product_id = dp.product_id
    INNER JOIN dbo.dim_category AS dc
        ON dp.category_id = dc.category_id
    WHERE fo.order_status = 'Completed'
    GROUP BY
        dc.category_id,
        dc.category_name,
        dp.product_id,
        dp.product_name
),
ranked_products AS (
    SELECT
        category_id,
        category_name,
        product_id,
        product_name,
        total_revenue,
        RANK() OVER (
            PARTITION BY category_id
            ORDER BY total_revenue DESC
        ) AS revenue_rank
    FROM product_revenue
)
SELECT
    category_id,
    category_name,
    product_id,
    product_name,
    total_revenue,
    revenue_rank
FROM ranked_products
WHERE revenue_rank <= 3
ORDER BY
    category_name,
    revenue_rank;