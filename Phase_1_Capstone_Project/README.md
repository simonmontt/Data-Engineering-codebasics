# AtliQ Commerce — Architecture and Nightly Synchronization

## Architecture Overview

The AtliQ Commerce solution separates the operational **OLTP** system from the analytical **OLAP** system so that reporting workloads do not affect the database used by the application. The OLTP database is optimized for frequent inserts and updates, while the OLAP layer is optimized for analytical queries and business reporting.

The source OLTP system is an **Azure SQL Database** named `atliq_commerce`. It uses a normalized 3NF model consisting of `customers`, `products`, `orders`, `order_items`, and `payments`. Orders and payments use `updated_at` as their incremental watermark, while the insert-only `order_items` table uses `created_at`. Smaller reference tables such as customers and products are reloaded in full. These ingestion rules are centralized in `etl.control_table`, which allows Azure Data Factory to use one generic metadata-driven pipeline instead of separate pipelines for every table.

The analytical side follows a medallion-style architecture:

```text
Azure SQL OLTP + CSV sources
            |
            v
   Azure Data Factory
            |
            v
     ADLS Bronze
      Parquet files
            |
            v
 Azure Databricks Silver
      Delta tables
            |
            v
        dbt Gold
       Star schema
            |
            v
 Databricks SQL Warehouse
            |
            v
 Power BI / Fabric Report
```

**Bronze** is the raw landing layer in Azure Data Lake Storage. Azure Data Factory reads `etl.control_table`, loops through the configured source tables, chooses full or incremental behavior, and writes Parquet data to Bronze. Incremental tables are stored in dated ingestion folders, while full-load reference data is overwritten.

**Silver** is implemented in Azure Databricks using Delta Lake. Full-load entities are cleaned and overwritten, while transactional entities are processed incrementally with Delta `MERGE`. `orders` and `payments` update existing business keys only when a newer record arrives, while `order_items` uses insert-only merge behavior. These rules make Silver idempotent, so rerunning the same batch does not create duplicate business records.

**Gold** is built with dbt as an OLAP star schema consisting of `fact_sales`, `dim_customer`, `dim_product`, and `dim_date`. `fact_sales` has one row per order item and contains analytical measures such as quantity, item price, and gross revenue. The dimensions provide customer, product, and calendar attributes, making analytical queries simpler and more efficient than querying the normalized OLTP schema directly.

## Nightly Synchronization

A scheduled **Azure Data Factory trigger runs the complete pipeline once every night**. At the beginning of each run, ADF records a common `run_start_at` timestamp and reads the ETL control table. Full-load tables are refreshed completely, while incremental tables extract only records whose watermark is newer than the previous successful load and no later than the current run boundary.

After Bronze ingestion succeeds, ADF triggers the Databricks workflow. The workflow first builds Silver and then executes `dbt build`, which creates the Gold models and runs the configured data-quality tests. Watermarks are advanced only after successful ingestion, while Delta `MERGE` and deterministic Gold rebuilds make the process safe to rerun.

End-to-end idempotency was validated by running the pipeline twice without adding new source transactions and confirming that the `fact_sales` row count and total revenue did not increase on the second execution.

For reporting, the Gold tables are queried through the **Databricks SQL Warehouse by the Power BI/Fabric semantic model**. Direct Lake through ADLS shortcuts and Unity Catalog mirroring was evaluated, but the environment could not frame the external Delta tables correctly even though SQL access and Unity Catalog permissions were valid. DirectQuery through the SQL Warehouse was therefore used as the reporting path without querying the production OLTP database.

Reliability is supported through **dbt tests, GitHub Actions CI, Azure Monitor failure alerts, and `etl.pipeline_audit`**. The audit table records each pipeline run ID, start and end times, final status, and source row counts, providing a simple operational history of the nightly synchronization process.
