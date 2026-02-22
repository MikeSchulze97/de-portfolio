# Spark Alignment Note (IU Concept Fit)

## Purpose
This project was designed as a batch-oriented data pipeline.  
To align the implementation with the submitted concept and architecture, the processing and aggregation steps are executed with Apache Spark (PySpark) in local mode.

Spark is used here as a batch processing engine (not streaming). The pipeline remains fully reproducible via Docker.

## Why Spark (and why local mode)
- Spark provides a clear, industry-standard model for batch transformations and aggregations (DataFrame API).
- Local mode is sufficient and appropriate for an IU portfolio project:
  - reproducible execution on a single machine
  - no cluster setup required
  - still demonstrates the Spark programming model (schema, transformations, aggregations, partitioned output)
- The focus is concept + implementation correctness, not scalability.

## Responsibilities (unchanged overall pipeline logic)
Ingestion stays unchanged:
- FastAPI receives HTTP events
- each event is stored as exactly one raw JSON file in `data/raw/`
- no transformation at ingestion time

Spark replaces the execution engine for:
- Batch processing (raw -> processed, partitioned by event time)
- Aggregation (processed -> aggregated event counts)
Optional serving layer:
- Postgres stores aggregated results to enable simple analytics queries

## Data Flow (Spark path)
1) `data/raw/*.json`  
2) Spark batch processing produces partitioned output in `data/processed/date=YYYY-MM-DD/hour=HH/`  
3) Spark aggregation reads processed partitions and produces:
   - file output: `data/aggregated/date=YYYY-MM-DD/hour=HH/event_counts.json` (transparent, inspectable)
   - optional DB output: Postgres table `event_counts` (analytics serving layer)

## Checkpointing / Idempotency
Checkpointing remains a mandatory part of the pipeline logic:
- processed raw file names are tracked to avoid duplicates across reruns
- aggregation state is tracked so only partitions with new data are recomputed (or forced)

## Out of Scope (still applies)
- no streaming platforms (Kafka, Kinesis)
- no message queues
- no cloud services
- no distributed cluster setup
- no performance optimization effort