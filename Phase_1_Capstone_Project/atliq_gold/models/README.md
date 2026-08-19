### dbt validation

The Gold layer is built with `dbt build`.

Tests include:
- unique and not-null `fact_sales.order_item_id`
- customer relationship to `dim_customer`
- product relationship to `dim_product`

The GitHub Actions CI workflow executes:

`dbt build --target ci`

on every pull request. The final CI run completed successfully with no test errors.