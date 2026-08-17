{{ config(materialized='table') }}

SELECT
    customer_id,
    customer_name,
    email,
    city,
    signup_date,
    CAST(DATE_TRUNC('MONTH', signup_date) AS DATE) AS signup_cohort

FROM {{ ref('stg_customers') }}