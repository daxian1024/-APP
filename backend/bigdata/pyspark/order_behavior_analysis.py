from pyspark.sql import SparkSession
from pyspark.sql.functions import count, avg


def run_analysis(input_path: str = "orders.parquet"):
    spark = SparkSession.builder.appName("SmartNursingOrderBehavior").getOrCreate()

    df = spark.read.parquet(input_path)

    status_dist = df.groupBy("status").agg(count("id").alias("cnt"))
    service_avg_price = df.groupBy("service_item_id").agg(avg("service_price").alias("avg_price"))

    status_dist.show(truncate=False)
    service_avg_price.show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    run_analysis()
