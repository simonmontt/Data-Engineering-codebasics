USE Voltkart;
GO

DECLARE @before_count int;
DECLARE @after_count int;

DECLARE @updated_sample TABLE (
    order_id int,
    old_order_status varchar(50),
    new_order_status varchar(50),
    old_order_total decimal(18, 2),
    new_order_total decimal(18, 2)
);

SELECT @before_count = COUNT(*)
FROM dbo.fact_orders;

INSERT INTO @updated_sample (
    order_id,
    old_order_status,
    new_order_status,
    old_order_total,
    new_order_total
)
SELECT TOP 20
    target.order_id,
    target.order_status,
    source.order_status,
    target.order_total,
    source.order_total
FROM dbo.fact_orders AS target
INNER JOIN dbo.stg_orders_incr AS source
    ON target.order_id = source.order_id
WHERE
       ISNULL(target.order_status, '') <> ISNULL(source.order_status, '')
    OR ISNULL(target.order_total, 0) <> ISNULL(source.order_total, 0)
ORDER BY target.order_id;

MERGE dbo.fact_orders AS target
USING dbo.stg_orders_incr AS source
    ON target.order_id = source.order_id

WHEN MATCHED AND (
       ISNULL(target.order_status, '') <> ISNULL(source.order_status, '')
    OR ISNULL(target.order_total, 0) <> ISNULL(source.order_total, 0)
)
THEN UPDATE SET
    target.order_status = source.order_status,
    target.order_total = source.order_total

WHEN NOT MATCHED BY TARGET
THEN INSERT (
    order_id,
    order_date,
    customer_id,
    sales_rep_id,
    order_status,
    order_total
)
VALUES (
    source.order_id,
    source.order_date,
    source.customer_id,
    source.sales_rep_id,
    source.order_status,
    source.order_total
);

SELECT @after_count = COUNT(*)
FROM dbo.fact_orders;

SELECT
    @before_count AS fact_orders_count_before,
    @after_count AS fact_orders_count_after,
    @after_count - @before_count AS rows_inserted;

SELECT
    order_id,
    old_order_status,
    new_order_status,
    old_order_total,
    new_order_total
FROM @updated_sample
ORDER BY order_id;