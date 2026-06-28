   SELECT o.customer_id, COUNT(*) AS orders_2024,
           (SELECT SUM(oi.line_amount)
              FROM fact_order_items oi
              JOIN fact_orders o2 ON o2.order_id = oi.order_id
             WHERE o2.customer_id = o.customer_id) AS lifetime_value
    FROM fact_orders o
    WHERE YEAR(o.order_date) = 2024
    GROUP BY o.customer_id;
    SET STATISTICS IO, TIME ON 