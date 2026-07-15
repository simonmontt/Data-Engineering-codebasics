SELECT
    a.airport_key,
    a.airport_code,
    a.airport_name,
    ci.city_name,
    c.country_name,
    c.region
FROM dw.DimAirport a
INNER JOIN dw.DimCity ci
    ON a.city_key = ci.city_key
INNER JOIN dw.DimCountry c
    ON ci.country_key = c.country_key
ORDER BY
    c.country_name,
    ci.city_name,
    a.airport_code;