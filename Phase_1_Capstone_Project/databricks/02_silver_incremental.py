# Databricks notebook source
from pyspark.sql import functions as F, Window
from delta.tables import DeltaTable

BRONZE = "abfss://atliqlakehouse@atliqstorage.dfs.core.windows.net/bronze"

# COMMAND ----------

# MAGIC %md
# MAGIC Create the run_date widget

# COMMAND ----------

dbutils.widgets.text("run_date", "", "Run date")

run_date = dbutils.widgets.get("run_date")

print("Run date:", run_date)

# COMMAND ----------

# MAGIC %md
# MAGIC Read Orders batch from run_date and inspection

# COMMAND ----------

src_path = f"{BRONZE}/orders/ingest_date={run_date}"
print(src_path)
batch = spark.read.parquet(src_path)

# COMMAND ----------

batch.printSchema()
print("Rows in Bronze batch:", batch.count())
display(batch)

# COMMAND ----------

for date in ["2026-08-13", "2026-08-14", "2026-08-15", "2026-08-16"]:
    print(f"\nDATE: {date}")

    for table in ["orders", "payments", "order_items"]:
        path = f"{BRONZE}/{table}/ingest_date={date}"

        try:
            count = spark.read.parquet(path).count()
            print(f"{table}: {count}")
        except:
            print(f"{table}: folder not found")

# COMMAND ----------

# MAGIC %md
# MAGIC Deduplicate the batch

# COMMAND ----------

w = (
    Window
        .partitionBy("order_id")
        .orderBy(F.col("updated_at").desc())
)

src = (
    batch
        .withColumn(
            "rn",
            F.row_number().over(w)
        )
        .filter(F.col("rn") == 1)
        .drop("rn")
        .withColumn(
            "order_date",
            F.to_date("order_date")
        )
        .withColumn(
            "order_amount",
            F.col("order_amount").cast("decimal(12,2)")
        )
        .filter(F.col("order_id").isNotNull())
)

# COMMAND ----------

# MAGIC %md
# MAGIC Inspect the cleaned batch

# COMMAND ----------

print("Bronze rows:", batch.count())
print("Rows after dedup:", src.count())

src.printSchema()
display(src)

# COMMAND ----------

# MAGIC %md
# MAGIC Create the Silver target if it doesn't exist

# COMMAND ----------

(
    DeltaTable
        .createIfNotExists(spark)
        .tableName("atliq.silver.orders")
        .addColumns(src.schema)
        .execute()
)

# COMMAND ----------

# MAGIC %md
# MAGIC MERGE into Silver

# COMMAND ----------

(
    DeltaTable
        .forName(spark, "atliq.silver.orders")
        .alias("t")
        .merge(
            src.alias("s"),
            "t.order_id = s.order_id"
        )
        .whenMatchedUpdateAll(
            condition="s.updated_at > t.updated_at"
        )
        .whenNotMatchedInsertAll()
        .execute()
)

# COMMAND ----------

# MAGIC %md
# MAGIC Verification

# COMMAND ----------

orders_silver = spark.table("atliq.silver.orders")

print("Silver orders:", orders_silver.count())

display(orders_silver)

# COMMAND ----------

duplicates = (
    orders_silver
        .groupBy("order_id")
        .count()
        .filter(F.col("count") > 1)
)

print("Duplicate order IDs:", duplicates.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Payments.
# MAGIC Inspection

# COMMAND ----------

payments_path = f"{BRONZE}/payments/ingest_date={run_date}"

payments_batch = spark.read.parquet(payments_path)

payments_batch.printSchema()
print("Bronze payments rows:", payments_batch.count())
display(payments_batch)

# COMMAND ----------

w_payments = (
    Window
        .partitionBy("payment_id")
        .orderBy(F.col("updated_at").desc())
)

payments_src = (
    payments_batch
        .withColumn(
            "rn",
            F.row_number().over(w_payments)
        )
        .filter(F.col("rn") == 1)
        .drop("rn")
        .filter(F.col("payment_id").isNotNull())
)

# COMMAND ----------

print("Payments before dedup:", payments_batch.count())
print("Payments after dedup:", payments_src.count())

display(payments_src)

# COMMAND ----------

(
    DeltaTable
        .createIfNotExists(spark)
        .tableName("atliq.silver.payments")
        .addColumns(payments_src.schema)
        .execute()
)

# COMMAND ----------

(
    DeltaTable
        .forName(spark, "atliq.silver.payments")
        .alias("t")
        .merge(
            payments_src.alias("s"),
            "t.payment_id = s.payment_id"
        )
        .whenMatchedUpdateAll(
            condition="s.updated_at > t.updated_at"
        )
        .whenNotMatchedInsertAll()
        .execute()
)

# COMMAND ----------

# MAGIC %md
# MAGIC Verification

# COMMAND ----------

payments_silver = spark.table("atliq.silver.payments")

print("Silver payments:", payments_silver.count())

display(payments_silver)

# COMMAND ----------

payment_duplicates = (
    payments_silver
        .groupBy("payment_id")
        .count()
        .filter(F.col("count") > 1)
)

print("Duplicate payment IDs:", payment_duplicates.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Order Items: Inspection

# COMMAND ----------

order_items_path = f"{BRONZE}/order_items/ingest_date={run_date}"

order_items_batch = spark.read.parquet(order_items_path)

order_items_batch.printSchema()
print("Bronze order_items rows:", order_items_batch.count())
display(order_items_batch)

# COMMAND ----------

w_order_items = (
    Window
        .partitionBy("order_item_id")
        .orderBy(F.col("created_at").desc())
)

order_items_src = (
    order_items_batch
        .withColumn(
            "rn",
            F.row_number().over(w_order_items)
        )
        .filter(F.col("rn") == 1)
        .drop("rn")
        .filter(F.col("order_item_id").isNotNull())
)

# COMMAND ----------

print("Order items before dedup:", order_items_batch.count())
print("Order items after dedup:", order_items_src.count())

display(order_items_src)

# COMMAND ----------

(
    DeltaTable
        .createIfNotExists(spark)
        .tableName("atliq.silver.order_items")
        .addColumns(order_items_src.schema)
        .execute()
)

# COMMAND ----------

(
    DeltaTable
        .forName(spark, "atliq.silver.order_items")
        .alias("t")
        .merge(
            order_items_src.alias("s"),
            "t.order_item_id = s.order_item_id"
        )
        .whenNotMatchedInsertAll()
        .execute()
)

# COMMAND ----------

# MAGIC %md
# MAGIC Verification

# COMMAND ----------

order_items_silver = spark.table("atliq.silver.order_items")

print("Silver order items:", order_items_silver.count())

display(order_items_silver)

# COMMAND ----------

order_item_duplicates = (
    order_items_silver
        .groupBy("order_item_id")
        .count()
        .filter(F.col("count") > 1)
)

print("Duplicate order_item IDs:", order_item_duplicates.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Verify all Silver Tables

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SHOW TABLES IN atliq.silver;

# COMMAND ----------

# MAGIC %md
# MAGIC Record the current Silver counts

# COMMAND ----------

tables = ["orders", "payments", "order_items"]

for table in tables:
    count = spark.table(f"atliq.silver.{table}").count()
    print(f"{table}: {count}")

# COMMAND ----------

# MAGIC %md
# MAGIC Check duplicate business keys

# COMMAND ----------

orders_duplicates = (
    spark.table("atliq.silver.orders")
        .groupBy("order_id")
        .count()
        .filter(F.col("count") > 1)
)

payments_duplicates = (
    spark.table("atliq.silver.payments")
        .groupBy("payment_id")
        .count()
        .filter(F.col("count") > 1)
)

order_items_duplicates = (
    spark.table("atliq.silver.order_items")
        .groupBy("order_item_id")
        .count()
        .filter(F.col("count") > 1)
)

print("Duplicate order items:", order_items_duplicates.count())
print("Duplicate payments:", payments_duplicates.count())
print("Duplicate orders:", orders_duplicates.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Check the counts again

# COMMAND ----------

for table in tables:
    count = spark.table(f"atliq.silver.{table}").count()
    print(f"{table}: {count}")