/* 
Initial load from bronze tables into dw star schema.
Assumption: dw tables already exist and are empty.
*/

-- 1. Load DimDate
INSERT INTO dw.DimDate (
    date_key,
    full_date,
    [year],
    [quarter],
    [month],
    month_name,
    [day],
    day_name
)
SELECT DISTINCT
    CONVERT(INT, CONVERT(CHAR(8), d.full_date, 112)) AS date_key,
    d.full_date,
    YEAR(d.full_date) AS [year],
    DATEPART(QUARTER, d.full_date) AS [quarter],
    MONTH(d.full_date) AS [month],
    DATENAME(MONTH, d.full_date) AS month_name,
    DAY(d.full_date) AS [day],
    DATENAME(WEEKDAY, d.full_date) AS day_name
FROM (
    SELECT booking_date AS full_date FROM dbo.bronze_bookings
    UNION
    SELECT travel_date FROM dbo.bronze_bookings
    UNION
    SELECT flight_date FROM dbo.bronze_flights
    UNION
    SELECT signup_date FROM dbo.bronze_passengers
) d
WHERE d.full_date IS NOT NULL;
GO

-- 2. Load DimAirport
INSERT INTO dw.DimAirport (
    airport_code,
    airport_name,
    city,
    country,
    region
)
SELECT
    airport_code,
    airport_name,
    city,
    country,
    region
FROM dbo.bronze_airports;
GO

-- 3. Load DimAircraft
INSERT INTO dw.DimAircraft (
    aircraft_code,
    model,
    manufacturer,
    seat_capacity
)
SELECT
    aircraft_code,
    model,
    manufacturer,
    seat_capacity
FROM dbo.bronze_aircraft;
GO

-- 4. Load DimPassenger
INSERT INTO dw.DimPassenger (
    passenger_id,
    passenger_name,
    home_airport_code,
    frequent_flyer_tier,
    signup_date
)
SELECT
    passenger_id,
    passenger_name,
    home_airport_code,
    frequent_flyer_tier,
    signup_date
FROM dbo.bronze_passengers;
GO

-- 5. Load DimFlight
INSERT INTO dw.DimFlight (
    flight_id,
    flight_number,
    origin_airport_code,
    dest_airport_code,
    aircraft_code,
    flight_date
)
SELECT
    flight_id,
    flight_number,
    origin_airport_code,
    dest_airport_code,
    aircraft_code,
    flight_date
FROM dbo.bronze_flights;
GO

-- 6. Load FactTicketSales
INSERT INTO dw.FactTicketSales (
    booking_id,
    booking_date_key,
    travel_date_key,
    passenger_key,
    flight_key,
    origin_airport_key,
    dest_airport_key,
    aircraft_key,
    ticket_count,
    fare_amount,
    tax_amount,
    miles_earned
)
SELECT
    b.booking_id,

    bd.date_key AS booking_date_key,
    td.date_key AS travel_date_key,

    p.passenger_key,
    f.flight_key,
    oa.airport_key AS origin_airport_key,
    da.airport_key AS dest_airport_key,
    ac.aircraft_key,

    1 AS ticket_count,
    b.fare_amount,
    b.tax_amount,
    b.miles_earned
FROM dbo.bronze_bookings b
INNER JOIN dbo.bronze_flights bf
    ON b.flight_id = bf.flight_id
INNER JOIN dw.DimDate bd
    ON b.booking_date = bd.full_date
INNER JOIN dw.DimDate td
    ON b.travel_date = td.full_date
INNER JOIN dw.DimPassenger p
    ON b.passenger_id = p.passenger_id
INNER JOIN dw.DimFlight f
    ON b.flight_id = f.flight_id
INNER JOIN dw.DimAirport oa
    ON bf.origin_airport_code = oa.airport_code
INNER JOIN dw.DimAirport da
    ON bf.dest_airport_code = da.airport_code
INNER JOIN dw.DimAircraft ac
    ON bf.aircraft_code = ac.aircraft_code;
GO

-- Fact row count should match bronze_bookings
SELECT 
    (SELECT COUNT(*) FROM dbo.bronze_bookings) AS bronze_booking_count,
    (SELECT COUNT(*) FROM dw.FactTicketSales) AS fact_ticket_sales_count;