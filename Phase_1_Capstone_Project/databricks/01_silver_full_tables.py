# Databricks notebook source
# MAGIC %md
# MAGIC Define the Bronze path & Read Bronze customers

# COMMAND ----------

from pyspark.sql import functions as F

BRONZE = "abfss://atliqlakehouse@atliqstorage.dfs.core.windows.net/bronze"
customers_bronze = spark.read.parquet(f"{BRONZE}/customers")
customers_bronze.printSchema()
display(customers_bronze)
customers_bronze.count()

# COMMAND ----------

# MAGIC %md
# MAGIC Clean the data

# COMMAND ----------

customers = (
    customers_bronze
        .withColumn("city", F.initcap(F.trim("city")))
        .withColumn("signup_date", F.to_date("signup_date"))
        .dropDuplicates(["customer_id"])
        .filter(F.col("customer_id").isNotNull())
)

# COMMAND ----------

# MAGIC %md
# MAGIC Inspect the cleaned result

# COMMAND ----------

customers.printSchema()
display(customers)
customers.count()
print("Bronze rows:", customers_bronze.count())
print("Silver rows:", customers.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Write Silver as Delta

# COMMAND ----------

(
    customers.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable("atliq.silver.customers")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Verify the Unity Catalog table

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT *
# MAGIC FROM atliq.silver.customers;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*)
# MAGIC FROM atliq.silver.customers;

# COMMAND ----------

# MAGIC %md
# MAGIC Products data. Inspection

# COMMAND ----------

products_bronze = spark.read.parquet(f"{BRONZE}/products")

products_bronze.printSchema()
display(products_bronze)

print("Bronze products:", products_bronze.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Products cleanup

# COMMAND ----------

products = (
    products_bronze
        .withColumn("product_name", F.trim("product_name"))
        .withColumn("category", F.initcap(F.trim("category")))
        .dropDuplicates(["product_id"])
        .filter(F.col("product_id").isNotNull())
)

products.printSchema()
display(products)

print("Silver products:", products.count())

# COMMAND ----------

(
    products.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable("atliq.silver.products")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Verification

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT COUNT(*)
# MAGIC FROM atliq.silver.products;

# COMMAND ----------

# MAGIC %md
# MAGIC Supplier price list: Inspection, clean and verification.

# COMMAND ----------

supplier_bronze = spark.read.parquet(
    f"{BRONZE}/supplier_price_list"
)

supplier_bronze.printSchema()
display(supplier_bronze)

# COMMAND ----------

supplier_price_list = (
    supplier_bronze
        .dropDuplicates(["product_id"])
        .filter(F.col("product_id").isNotNull())
)

# COMMAND ----------

(
    supplier_price_list.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable("atliq.silver.supplier_price_list")
)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT *
# MAGIC FROM atliq.silver.supplier_price_list;

# COMMAND ----------

# MAGIC %md
# MAGIC Marketing spend: Inspection, clean and verification.

# COMMAND ----------

marketing_bronze = spark.read.parquet(
    f"{BRONZE}/marketing_spend"
)

marketing_bronze.printSchema()
display(marketing_bronze)

print("Bronze marketing rows:", marketing_bronze.count())

# COMMAND ----------

marketing_spend = marketing_bronze

(
    marketing_spend.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable("atliq.silver.marketing_spend")
)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT *
# MAGIC FROM atliq.silver.marketing_spend;

# COMMAND ----------

# MAGIC %md
# MAGIC Verify all four Full Silver tables
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SHOW TABLES IN atliq.silver;