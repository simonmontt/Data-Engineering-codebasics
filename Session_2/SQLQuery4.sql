/*
Question 4 correction:
Snowflake the existing dw.DimAirport into:

DimCountry -> DimCity -> DimAirport

We do NOT recreate DimAirport because it already exists from Question 2.
*/

-- 1. Create DimCountry
IF OBJECT_ID('dw.DimCountry', 'U') IS NULL
BEGIN
    CREATE TABLE dw.DimCountry (
        country_key   INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        country_name  VARCHAR(100)      NOT NULL,
        region        VARCHAR(100)      NOT NULL,

        CONSTRAINT UQ_DimCountry_CountryName
            UNIQUE (country_name)
    );
END;
GO

-- 2. Load countries
INSERT INTO dw.DimCountry (
    country_name,
    region
)
SELECT DISTINCT
    country,
    region
FROM dbo.bronze_airports ba
WHERE NOT EXISTS (
    SELECT 1
    FROM dw.DimCountry c
    WHERE c.country_name = ba.country
);
GO

-- 3. Create DimCity
IF OBJECT_ID('dw.DimCity', 'U') IS NULL
BEGIN
    CREATE TABLE dw.DimCity (
        city_key     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        city_name    VARCHAR(100)      NOT NULL,
        country_key  INT               NOT NULL,

        CONSTRAINT FK_DimCity_Country
            FOREIGN KEY (country_key) REFERENCES dw.DimCountry(country_key),

        CONSTRAINT UQ_DimCity_CityCountry
            UNIQUE (city_name, country_key)
    );
END;
GO

-- 4. Load cities
INSERT INTO dw.DimCity (
    city_name,
    country_key
)
SELECT DISTINCT
    ba.city,
    c.country_key
FROM dbo.bronze_airports ba
INNER JOIN dw.DimCountry c
    ON ba.country = c.country_name
WHERE NOT EXISTS (
    SELECT 1
    FROM dw.DimCity ci
    WHERE ci.city_name = ba.city
      AND ci.country_key = c.country_key
);
GO

-- 5. Add city_key to the existing DimAirport
IF COL_LENGTH('dw.DimAirport', 'city_key') IS NULL
BEGIN
    ALTER TABLE dw.DimAirport
    ADD city_key INT NULL;
END;
GO

-- 6. Populate city_key in existing DimAirport
UPDATE a
SET a.city_key = ci.city_key
FROM dw.DimAirport a
INNER JOIN dbo.bronze_airports ba
    ON a.airport_code = ba.airport_code
INNER JOIN dw.DimCountry c
    ON ba.country = c.country_name
INNER JOIN dw.DimCity ci
    ON ba.city = ci.city_name
   AND c.country_key = ci.country_key;
GO

-- 7. Make city_key mandatory after it has been populated
IF NOT EXISTS (
    SELECT 1
    FROM dw.DimAirport
    WHERE city_key IS NULL
)
BEGIN
    ALTER TABLE dw.DimAirport
    ALTER COLUMN city_key INT NOT NULL;
END;
GO

-- 8. Add the foreign key from Airport to City
IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_DimAirport_City'
      AND parent_object_id = OBJECT_ID('dw.DimAirport')
)
BEGIN
    ALTER TABLE dw.DimAirport
    ADD CONSTRAINT FK_DimAirport_City
        FOREIGN KEY (city_key) REFERENCES dw.DimCity(city_key);
END;
GO