CREATE PARTITION FUNCTION pf_FactTicketSales_BookingDateKey (INT)
AS RANGE RIGHT FOR VALUES (
    20240101, 20240201, 20240301, 20240401,
    20240501, 20240601, 20240701, 20240801,
    20240901, 20241001, 20241101, 20241201,
    20250101
);
GO

CREATE PARTITION SCHEME ps_FactTicketSales_BookingDateKey
AS PARTITION pf_FactTicketSales_BookingDateKey
ALL TO ([PRIMARY]);
GO

-- Find and drop the existing primary key
DECLARE @pk_name SYSNAME;
DECLARE @sql NVARCHAR(MAX);

SELECT @pk_name = kc.name
FROM sys.key_constraints kc
WHERE kc.parent_object_id = OBJECT_ID('dw.FactTicketSales')
  AND kc.type = 'PK';

IF @pk_name IS NOT NULL
BEGIN
    SET @sql =
        N'ALTER TABLE dw.FactTicketSales DROP CONSTRAINT '
        + QUOTENAME(@pk_name) + N';';

    EXEC sys.sp_executesql @sql;
END;
GO

-- Recreate the primary key on the partition scheme
ALTER TABLE dw.FactTicketSales
ADD CONSTRAINT PK_FactTicketSales_Q6
PRIMARY KEY CLUSTERED (
    booking_date_key,
    ticket_sales_key
)
ON ps_FactTicketSales_Q6(booking_date_key);
GO

-- JUST to Check the fact is now partitioned

/* SELECT
    i.name AS index_name,
    ds.name AS storage_location,
    ds.type_desc
FROM sys.indexes i
INNER JOIN sys.data_spaces ds
    ON i.data_space_id = ds.data_space_id
WHERE i.object_id = OBJECT_ID('dw.FactTicketSales')
  AND i.index_id = 1;
*/