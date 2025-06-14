from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    window,
    count,
    from_json,
    floor,
    col,
    unix_timestamp,
    from_unixtime,
    to_timestamp,
    when,
    to_json,
    struct,
)

from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType


spark = SparkSession.builder.appName("EmoSteam").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


schema = (
    StructType()
    .add("user", StringType())
    .add("emoji_name", StringType())
    .add("emoji", StringType())
    .add("timestamp", TimestampType())
)


df_kafka = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "topic1")
    .load()
)

df_parsed = (
    df_kafka.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
    .withColumn("json", from_json(col("value"), schema))
    .select("key", "json.*")
)

windowed_batch = df_parsed.groupBy(
    window(col("timestamp"), "2 seconds"), col("emoji_name"), col("emoji")
).agg(count("*").alias("e_count"))


scaled_batch = windowed_batch.withColumn(
    "scaled_count", when(col("e_count") >= 25, 1).otherwise(0)
)


output = scaled_batch.filter(col("scaled_count") == 1).select(
    to_json(
        struct(
            col("window.start").alias("start"),
            col("window.end").alias("end"),
            col("emoji_name"),
            col("emoji"),
            col("scaled_count"),
        )
    ).alias("value")
)


query = (
    output.writeStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("topic", "topic2")
    .outputMode("append")
    .start()
)

query.awaitTermination()
