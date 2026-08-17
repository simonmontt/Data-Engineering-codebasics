SELECT *
FROM {{ source('silver', 'products') }}