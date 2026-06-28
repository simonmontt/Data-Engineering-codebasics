USE Voltkart;
GO

SELECT TOP 20
    fo.order_id,
    fo.order_date,
    dc.customer_name,
    de.employee_name AS sales_rep_name,
    fo.order_total
FROM dbo.fact_orders AS fo
INNER JOIN dbo.dim_customer AS dc
    ON fo.customer_id = dc.customer_id
INNER JOIN dbo.dim_employee AS de
    ON fo.sales_rep_id = de.employee_id
WHERE fo.order_status = 'Completed'
ORDER BY fo.order_total DESC;