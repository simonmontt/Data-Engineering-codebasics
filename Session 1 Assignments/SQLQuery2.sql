USE Voltkart;
GO

SELECT
    dc.customer_id,
    dc.customer_name,
    dc.signup_date
FROM dbo.dim_customer AS dc
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.fact_orders AS fo
    WHERE fo.customer_id = dc.customer_id
);