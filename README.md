# Data Engineering Portfolio – Batch Event Pipeline (IU)

This project is a **Data Engineering examination project** created as part of the IU curriculum.

The goal of the project is to demonstrate **conceptual understanding and technical implementation of a complete batch-based data pipeline**, from ingestion to aggregation, using transparent and reproducible mechanisms.

The project intentionally focuses on **fundamental data engineering principles** rather than performance, scalability or production readiness.

---

## Project Goal & Scope

This project demonstrates:

- an end-to-end batch pipeline
- clear separation of ingestion, processing and aggregation
- event-time driven data handling
- explicit state management via checkpoints
- deterministic and reproducible execution

The project is **not** intended to be a production system.  
All design decisions are consciously simplified to ensure **traceability and inspectability**, which is essential in an academic context.

---

## What Is Executed in This Project

The pipeline consists of **two types of components**:

### Long-running service
- **Ingestion Service (FastAPI)**  
  Receives events via HTTP and persists them as raw JSON files.

### Batch jobs
- **Batch Processing (`run_batch.py`)**  
  Processes raw events into partitioned, validated datasets.
- **Aggregation (`run_aggregate.py`)**  
  Aggregates processed events into final result files.

All components are executed **exclusively via Docker and Docker Compose**.  
No local Python environment is required.

---

## Architecture Overview

The pipeline follows a linear, batch-oriented architecture:

CSV Input  
→ Event Generator  
→ Ingestion Service (FastAPI)  
→ `data/raw/`  
→ Batch Processing  
→ `data/processed/date=YYYY-MM-DD/hour=HH/`  
→ Aggregation  
→ `data/aggregated/`

All intermediate and final data is stored on the local filesystem to ensure full transparency.

---

## Data Flow

### Ingestion

- Events are sent via HTTP POST to the ingestion service.
- Each event is written **unchanged** as a single JSON file.
- No transformation or validation happens at this stage.

Event time is encoded in the filename.

Example filename: 
20260210T1015001234_ecommerce_transaction.json

---

### Batch Processing

The batch processor:

- reads raw JSON event files
- validates schema and structure
- extracts event time from filenames
- writes valid events as JSON Lines (`events.jsonl`)
- partitions data by `date=YYYY-MM-DD/hour=HH`
- tracks processed files using an explicit checkpoint

Handled scenarios:

- invalid schema → quarantined
- malformed JSON → quarantined
- already processed files → skipped
- late-arriving events → written to historical partitions

Checkpoint file: data/_checkpoints/processed_raw_files.txt

Raw data is never modified.

---

### Aggregation

The aggregation step:

- reads `events.jsonl` per partition
- aggregates events by `event_type`
- writes results to `event_counts.json`
- tracks aggregation state via partition modification timestamps

State file: 
data/_checkpoints/aggregated_partitions_state.json

Only partitions with new or changed data are recomputed unless `--force` is used.

---

## State Management & Reproducibility

State is handled explicitly via checkpoint files.

This ensures:

- idempotent batch execution
- no duplicate processing
- deterministic results across multiple runs
- safe re-execution after restarts

The pipeline can be stopped, restarted and re-run without manual cleanup.

---

## Directory Structure

data/
├── raw/
├── processed/
│ └── date=YYYY-MM-DD/
│ └── hour=HH/
│ └── events.jsonl
├── aggregated/
│ └── date=YYYY-MM-DD/
│ └── hour=HH/
│ └── event_counts.json
└── _checkpoints/
├── processed_raw_files.txt
└── aggregated_partitions_state.json

---

## Running and Verifying the Pipeline (Docker)

All interactions are executed via a PowerShell helper script.

Start ingestion service: 
.\tasks_docker.ps1 up

Swagger UI: 
http://localhost:8000/docs

Run batch processing: 
.\tasks_docker.ps1 batch
.\tasks_docker.ps1 batch -Limit 50

List processed partitions:
.\tasks_docker.ps1 partitions

Run aggregation:
.\tasks_docker.ps1 aggregate
.\tasks_docker.ps1 aggregate -Force

Stop all containers:
.\tasks_docker.ps1 down

Repeated executions do not create duplicates and respect existing checkpoints.

---

## Design Decisions (Conceptual Rationale)

- Batch-oriented design to focus on deterministic processing logic
- Filesystem-based storage for full transparency and inspectability
- Explicit checkpoints instead of implicit idempotency
- Event-time partitioning to correctly handle late-arriving data
- Docker-only execution for reproducibility and consistent evaluation

These decisions prioritize **clarity and traceability** over scalability or performance.

---

## Scope & Explicit Limitations

This project intentionally excludes:

- streaming platforms (Kafka, Kinesis)
- distributed storage (S3, HDFS)
- orchestration frameworks (Airflow, Prefect)
- schema registries
- visualization or BI layers

The scope is deliberately constrained to demonstrate **core batch data engineering concepts** in a controlled and inspectable environment.