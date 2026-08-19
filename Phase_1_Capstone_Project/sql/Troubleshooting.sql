SELECT table_name, last_loaded_at
FROM etl.control_table
WHERE table_name IN ('orders', 'order_items', 'payments');