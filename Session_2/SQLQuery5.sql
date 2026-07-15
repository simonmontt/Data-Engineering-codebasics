IF COL_LENGTH('dw.DimPassenger', 'effective_from') IS NULL
    ALTER TABLE dw.DimPassenger ADD effective_from DATETIME2(0) NULL;
GO
 
IF COL_LENGTH('dw.DimPassenger', 'effective_to') IS NULL
    ALTER TABLE dw.DimPassenger ADD effective_to DATETIME2(0) NULL;
GO
 
IF COL_LENGTH('dw.DimPassenger', 'is_current') IS NULL
    ALTER TABLE dw.DimPassenger ADD is_current BIT NULL;
GO
 
UPDATE dw.DimPassenger
SET effective_from = CAST(signup_date AS DATETIME2(0)),
    effective_to = NULL,
    is_current = 1
WHERE effective_from IS NULL OR is_current IS NULL;
GO
 
ALTER TABLE dw.DimPassenger ALTER COLUMN effective_from DATETIME2(0) NOT NULL;
ALTER TABLE dw.DimPassenger ALTER COLUMN is_current BIT NOT NULL;
GO

CREATE UNIQUE INDEX UX_DimPassenger_Current
ON dw.DimPassenger(passenger_id)
WHERE is_current = 1;
GO
DECLARE @load_datetime DATETIME2(0) = SYSUTCDATETIME();
 
DROP TABLE IF EXISTS #passenger_changes;
 
SELECT DISTINCT
    s.passenger_id,
    s.passenger_name,
    s.home_airport_code,
    s.frequent_flyer_tier
INTO #passenger_changes
FROM dbo.stg_passenger_updates s
JOIN dw.DimPassenger d
    ON s.passenger_id = d.passenger_id
   AND d.is_current = 1
WHERE COALESCE(s.home_airport_code, '###') <> COALESCE(d.home_airport_code, '###')
   OR COALESCE(s.frequent_flyer_tier, '###') <> COALESCE(d.frequent_flyer_tier, '###');
 
UPDATE d
SET d.is_current = 0,
    d.effective_to = @load_datetime
FROM dw.DimPassenger d
JOIN #passenger_changes c ON d.passenger_id = c.passenger_id
WHERE d.is_current = 1;
 
INSERT INTO dw.DimPassenger (
    passenger_id, passenger_name, home_airport_code, frequent_flyer_tier,
    signup_date, effective_from, effective_to, is_current
)
SELECT
    passenger_id, passenger_name, home_airport_code, frequent_flyer_tier,
    NULL, @load_datetime, NULL, 1
FROM #passenger_changes;
