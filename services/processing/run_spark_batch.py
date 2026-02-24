from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, date_format, input_file_name, regexp_extract
from pathlib import Path
import os

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def main() -> None:
    spark = SparkSession.builder.appName("SparkBatchProcessing").master("local[*]").getOrCreate()

    raw_path = str(RAW_DIR / "*.json")
    df = spark.read.json(raw_path)

    df = df.filter(col("event_type").isNotNull() & col("payload").isNotNull())

    df = df.withColumn("source_file", input_file_name())
    df = df.withColumn("ts_prefix", regexp_extract(col("source_file"), r"(\d{8}T\d{6}\d{6})_", 1))

    df = df.withColumn("event_time", to_timestamp(col("ts_prefix"), "yyyyMMdd'T'HHmmssSSSSSS"))

    df = df.withColumn("date", date_format(col("event_time"), "yyyy-MM-dd")).withColumn("hour", date_format(col("event_time"), "HH"))

    valid_df = df.filter(col("event_time").isNotNull() & col("date").isNotNull() & col("hour").isNotNull())

    total = df.count()
    valid = valid_df.count()
    dropped = total - valid
    print(f"[SparkBatch] total={total}, valid={valid}, dropped_invalid_partitions={dropped}")

    (
        valid_df.select("event_type", "event_time", "payload", "ts_prefix", "source_file", "date", "hour")
        .write.mode("append")
        .partitionBy("date", "hour")
        .json(str(PROCESSED_DIR))
    )

    spark.stop()


if __name__ == "__main__":
    main()