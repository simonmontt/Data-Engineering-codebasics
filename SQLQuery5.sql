USE Voltkart;
GO

WITH customer_lifetime_spend AS (
    SELECT
        dc.customer_id,
        dc.customer_name,
        COALESCE(SUM(fo.order_total), 0) AS lifetime_completed_spend
    FROM dbo.dim_customer AS dc
    LEFT JOIN dbo.fact_orders AS fo
        ON dc.customer_id = fo.customer_id
        AND fo.order_status = 'Completed'
    GROUP BY
        dc.customer_id,
        dc.customer_name
),
customer_quartiles AS (
    SELECT
        customer_id,
        customer_name,
        lifetime_completed_spend,
        NTILE(4) OVER (
            ORDER BY lifetime_completed_spend DESC
        ) AS spend_quartile
    FROM customer_lifetime_spend
)
SELECT
    spend_quartile,
    COUNT(*) AS customer_count,
    AVG(lifetime_completed_spend) AS avg_lifetime_spend
FROM customer_quartiles
GROUP BY
    spend_quartile
ORDER BY
    spend_quartile;