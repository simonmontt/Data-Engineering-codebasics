USE Voltkart;
GO

WITH category_subtree AS (
    SELECT
        category_id,
        category_name,
        parent_category_id,
        0 AS depth_level,
        CAST(category_name AS varchar(500)) AS category_path
    FROM dbo.dim_category
    WHERE category_name = 'Computers'

    UNION ALL

    SELECT
        child.category_id,
        child.category_name,
        child.parent_category_id,
        parent.depth_level + 1 AS depth_level,
        CAST(parent.category_path + ' > ' + child.category_name AS varchar(500)) AS category_path
    FROM dbo.dim_category AS child
    INNER JOIN category_subtree AS parent
        ON child.parent_category_id = parent.category_id
)
SELECT
    category_id,
    category_name,
    depth_level,
    category_path
FROM category_subtree
ORDER BY
    category_path
OPTION (MAXRECURSION 0);