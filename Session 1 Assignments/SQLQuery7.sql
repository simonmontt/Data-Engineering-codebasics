USE Voltkart;
GO

WITH employee_tree AS (
    -- Every employee belongs to their own team
    SELECT
        employee_id AS manager_employee_id,
        employee_id AS team_member_employee_id
    FROM dbo.dim_employee

    UNION ALL

    -- Add everyone reporting under each team member
    SELECT
        et.manager_employee_id,
        child.employee_id AS team_member_employee_id
    FROM employee_tree AS et
    INNER JOIN dbo.dim_employee AS child
        ON child.manager_id = et.team_member_employee_id
),
team_revenue AS (
    SELECT
        et.manager_employee_id AS employee_id,
        SUM(fo.order_total) AS team_total_revenue
    FROM employee_tree AS et
    INNER JOIN dbo.fact_orders AS fo
        ON fo.sales_rep_id = et.team_member_employee_id
    WHERE fo.order_status = 'Completed'
    GROUP BY
        et.manager_employee_id
)
SELECT
    de.employee_id,
    de.employee_name,
    de.role,
    COALESCE(tr.team_total_revenue, 0) AS team_total_revenue
FROM dbo.dim_employee AS de
LEFT JOIN team_revenue AS tr
    ON de.employee_id = tr.employee_id
ORDER BY
    team_total_revenue DESC
OPTION (MAXRECURSION 0);