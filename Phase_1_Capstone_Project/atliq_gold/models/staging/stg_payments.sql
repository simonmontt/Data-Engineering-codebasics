SELECT *
FROM {{ source('silver', 'payments') }}