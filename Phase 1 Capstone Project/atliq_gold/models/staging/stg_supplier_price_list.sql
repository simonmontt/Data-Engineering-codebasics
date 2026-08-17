SELECT *
FROM {{ source('silver', 'supplier_price_list') }}