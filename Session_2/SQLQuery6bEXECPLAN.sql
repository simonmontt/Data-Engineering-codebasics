-- Partition-key filter: should prune partitions
SELECT COUNT_BIG(*) AS partition_key_count
FROM dw.FactTicketSales
WHERE booking_date_key >= 20241201
  AND booking_date_key < 20250101
OPTION (RECOMPILE);

-- Non-partition filter: should access multiple partitions
SELECT COUNT_BIG(*) AS non_partition_key_count
FROM dw.FactTicketSales
WHERE travel_date_key >= 20241201
  AND travel_date_key < 20250101
OPTION (RECOMPILE);