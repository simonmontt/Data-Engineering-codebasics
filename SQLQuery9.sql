USE Voltkart;
GO

DECLARE @change_verification TABLE (
    applied_action varchar(10),
    product_id int,
    old_product_name varchar(100),
    new_product_name varchar(100),
    old_unit_price decimal(18, 2),
    new_unit_price decimal(18, 2)
);

WITH latest_changes AS (
    SELECT
        change_id,
        product_id,
        operation,
        change_ts,
        product_name,
        category_id,
        unit_price,
        unit_cost,
        launch_date,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY change_ts DESC, change_id DESC
        ) AS rn
    FROM dbo.cdc_product_changes
)
INSERT INTO @change_verification
SELECT
    CASE
        WHEN lc.operation = 'I' AND dp.product_id IS NULL THEN 'INSERT'
        WHEN lc.operation = 'U' AND dp.product_id IS NOT NULL THEN 'UPDATE'
        WHEN lc.operation = 'D' AND dp.product_id IS NOT NULL THEN 'DELETE'
    END AS applied_action,
    lc.product_id,
    dp.product_name AS old_product_name,
    lc.product_name AS new_product_name,
    dp.unit_price AS old_unit_price,
    lc.unit_price AS new_unit_price
FROM latest_changes AS lc
LEFT JOIN dbo.dim_product AS dp
    ON lc.product_id = dp.product_id
WHERE lc.rn = 1
  AND (
        (lc.operation = 'I' AND dp.product_id IS NULL)
     OR (lc.operation = 'U' AND dp.product_id IS NOT NULL)
     OR (lc.operation = 'D' AND dp.product_id IS NOT NULL)
  );

MERGE dbo.dim_product AS target
USING (
    SELECT
        product_id,
        operation,
        product_name,
        category_id,
        unit_price,
        unit_cost,
        launch_date
    FROM (
        SELECT
            product_id,
            operation,
            product_name,
            category_id,
            unit_price,
            unit_cost,
            launch_date,
            ROW_NUMBER() OVER (
                PARTITION BY product_id
                ORDER BY change_ts DESC, change_id DESC
            ) AS rn
        FROM dbo.cdc_product_changes
    ) AS ranked_changes
    WHERE rn = 1
) AS source
    ON target.product_id = source.product_id

WHEN MATCHED AND source.operation = 'U'
THEN UPDATE SET
    target.product_name = source.product_name,
    target.category_id = source.category_id,
    target.unit_price = source.unit_price,
    target.unit_cost = source.unit_cost,
    target.launch_date = source.launch_date

WHEN MATCHED AND source.operation = 'D'
THEN DELETE

WHEN NOT MATCHED BY TARGET AND source.operation = 'I'
THEN INSERT (
    product_id,
    product_name,
    category_id,
    unit_price,
    unit_cost,
    launch_date
)
VALUES (
    source.product_id,
    source.product_name,
    source.category_id,
    source.unit_price,
    source.unit_cost,
    source.launch_date
);

SELECT
    applied_action,
    COUNT(*) AS product_count
FROM @change_verification
GROUP BY applied_action;

SELECT
    applied_action,
    product_id,
    old_product_name,
    new_product_name,
    old_unit_price,
    new_unit_price
FROM @change_verification
ORDER BY
    applied_action,
    product_id;