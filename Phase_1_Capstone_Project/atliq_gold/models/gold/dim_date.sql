{{ config(materialized='table') }}

WITH date_spine AS (

    SELECT EXPLODE(
        SEQUENCE(
            TO_DATE('2024-01-01'),
            TO_DATE('2026-12-31'),
            INTERVAL 1 DAY
        )
    ) AS date_day

)

SELECT
    date_day,
    DAY(date_day) AS day,
    MONTH(date_day) AS month,
    DATE_FORMAT(date_day, 'MMMM') AS month_name,
    QUARTER(date_day) AS quarter,
    YEAR(date_day) AS year,
    DATE_FORMAT(date_day, 'EEEE') AS weekday

FROM date_spine