SELECT passenger_id, COUNT(*) AS current_version_count
FROM dw.DimPassenger
WHERE is_current = 1
GROUP BY passenger_id
HAVING COUNT(*) <> 1;
