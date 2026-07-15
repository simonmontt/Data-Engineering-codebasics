-- Grain: one row in dw.FactTicketSales represents one passenger ticket booking for one scheduled flight.

CREATE SCHEMA dw;
GO

CREATE TABLE dw.DimDate (
    date_key        INT          NOT NULL PRIMARY KEY, -- e.g. 20260131
    full_date       DATE         NOT NULL UNIQUE,
    [year]          INT          NOT NULL,
    [quarter]       INT          NOT NULL,
    [month]         INT          NOT NULL,
    month_name      VARCHAR(20)  NOT NULL,
    [day]           INT          NOT NULL,
    day_name        VARCHAR(20)  NOT NULL
);
GO

CREATE TABLE dw.DimPassenger (
    passenger_key        INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    passenger_id         INT               NOT NULL, -- business key
    passenger_name       VARCHAR(200)      NOT NULL,
    home_airport_code    CHAR(3)           NULL,
    frequent_flyer_tier  VARCHAR(30)       NULL,
    signup_date          DATE              NULL
);
GO

CREATE TABLE dw.DimAirport (
    airport_key    INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    airport_code   CHAR(3)           NOT NULL UNIQUE, -- business key
    airport_name   VARCHAR(200)      NOT NULL,
    city           VARCHAR(100)      NOT NULL,
    country        VARCHAR(100)      NOT NULL,
    region         VARCHAR(100)      NOT NULL
);
GO

CREATE TABLE dw.DimAircraft (
    aircraft_key   INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    aircraft_code  VARCHAR(20)       NOT NULL UNIQUE, -- business key
    model          VARCHAR(100)      NOT NULL,
    manufacturer   VARCHAR(100)      NOT NULL,
    seat_capacity  INT               NOT NULL
);
GO

CREATE TABLE dw.DimFlight (
    flight_key           INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    flight_id            INT               NOT NULL UNIQUE, -- business key
    flight_number        VARCHAR(20)       NOT NULL,
    origin_airport_code  CHAR(3)           NOT NULL,
    dest_airport_code    CHAR(3)           NOT NULL,
    aircraft_code        VARCHAR(20)       NOT NULL,
    flight_date          DATE              NOT NULL
);
GO

CREATE TABLE dw.FactTicketSales (
    ticket_sales_key      BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,

    -- Degenerate dimension: business transaction id kept directly on the fact
    booking_id            INT NOT NULL,

    -- Surrogate-key foreign keys to dimensions
    booking_date_key      INT NOT NULL,
    travel_date_key       INT NOT NULL,
    passenger_key         INT NOT NULL,
    flight_key            INT NOT NULL,
    origin_airport_key    INT NOT NULL,
    dest_airport_key      INT NOT NULL,
    aircraft_key          INT NOT NULL,

    -- Additive measures only
    ticket_count          INT NOT NULL DEFAULT 1,
    fare_amount           DECIMAL(18,2) NOT NULL,
    tax_amount            DECIMAL(18,2) NOT NULL,
    miles_earned          INT NOT NULL,

    CONSTRAINT FK_FactTicketSales_BookingDate
        FOREIGN KEY (booking_date_key) REFERENCES dw.DimDate(date_key),

    CONSTRAINT FK_FactTicketSales_TravelDate
        FOREIGN KEY (travel_date_key) REFERENCES dw.DimDate(date_key),

    CONSTRAINT FK_FactTicketSales_Passenger
        FOREIGN KEY (passenger_key) REFERENCES dw.DimPassenger(passenger_key),

    CONSTRAINT FK_FactTicketSales_Flight
        FOREIGN KEY (flight_key) REFERENCES dw.DimFlight(flight_key),

    CONSTRAINT FK_FactTicketSales_OriginAirport
        FOREIGN KEY (origin_airport_key) REFERENCES dw.DimAirport(airport_key),

    CONSTRAINT FK_FactTicketSales_DestAirport
        FOREIGN KEY (dest_airport_key) REFERENCES dw.DimAirport(airport_key),

    CONSTRAINT FK_FactTicketSales_Aircraft
        FOREIGN KEY (aircraft_key) REFERENCES dw.DimAircraft(aircraft_key)
);
GO