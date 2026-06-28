USE Voltkart;
GO

WITH monthly_revenue AS (
    SELECT
        CONVERT(char(7), order_date, 126) AS order_month,
        SUM(order_total) AS monthly_revenue
    FROM dbo.fact_orders
    WHERE order_status = 'Completed'
    GROUP BY
        CONVERT(char(7), order_date, 126)
),
monthly_with_windows AS (
    SELECT
        order_month,
        monthly_revenue,
        SUM(monthly_revenue) OVER (
            ORDER BY order_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_total,
        LAG(monthly_revenue) OVER (
            ORDER BY order_month
        ) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    order_month,
    monthly_revenue,
    running_total,
    CASE
        WHEN previous_month_revenue IS NULL THEN NULL
        WHEN previous_month_revenue = 0 THEN NULL
        ELSE
            ((monthly_revenue - previous_month_revenue) * 100.0)
            / previous_month_revenue
    END AS mom_pct_change
FROM monthly_with_windows
ORDER BY order_month;