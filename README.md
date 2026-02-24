# Data Engineering Portfolio – Batch Event Pipeline

This project was created as part of the **Data Engineering portfolio assessment** at IU.

The goal of the project is to demonstrate a **batch-based data pipeline**, covering the full process from data ingestion to aggregation.

The focus is on **conceptual clarity, traceability and reproducibility**, not on performance, scalability or production-level complexity.

---

## Project Overview

The project implements a batch-oriented data pipeline that:

- receives events via an API  
- stores raw data unchanged  
- processes events in batches  
- aggregates results per time window  
- can be re-run deterministically  

All steps are designed to be **easy to follow and inspect**, which is especially important in an academic context.

---

## Pipeline Structure

The pipeline consists of the following components:

### Ingestion Service
- A small FastAPI service that receives events via HTTP  
- Each incoming event is stored as a raw JSON file  
- No validation or transformation happens at this stage  

### Batch Processing (Spark)
- Reads raw event files  
- Extracts event time from filenames  
- Structures and validates the data  
- Writes processed events into time-based partitions  

### Aggregation (Spark)
- Reads processed data per partition  
- Aggregates events by event type  
- Writes the final results as JSON files  

All components are executed using **Docker and Docker Compose** to ensure consistent and reproducible execution.

---

## Architecture

The data flows through the system as follows:

Event Generator  
→ Ingestion Service (FastAPI)  
→ Raw data storage  
→ Batch Processing (Spark)  
→ Processed data (partitioned by date and hour)  
→ Aggregation (Spark)  
→ Aggregated result files  

All data is stored locally on the filesystem to make every step transparent and easy to inspect.

---

## Data Handling

### Raw Data
- Each event is stored as a single JSON file  
- Event time is encoded in the filename  
- Raw files are never modified after ingestion  

### Processed Data
- Valid events are written to partitioned folders:
  - `date=YYYY-MM-DD/hour=HH`
- Partitioning is based on event time  
- Invalid or incomplete events are excluded from further processing  

### Aggregated Data
- For each partition, events are counted by event type  
- Results are written to `event_counts.json`  

---

## Checkpoints and Reproducibility

The pipeline uses simple checkpoint files to track progress.

This ensures that:
- already processed data is not duplicated  
- batch jobs can be safely re-run  
- the pipeline can be stopped and restarted without manual cleanup  

The behaviour remains consistent across multiple executions.

---

## Directory Structure (Simplified)

data/
├── raw/
├── processed/
│ └── date=YYYY-MM-DD/
│ └── hour=HH/
├── aggregated/
│ └── date=YYYY-MM-DD/
│ └── hour=HH/
└── _checkpoints/

Generated data folders are excluded from version control.

---

## Running the Pipeline

All commands are executed via a PowerShell helper script.

Start the ingestion service:
.\tasks_docker.ps1 up

Access API documentation:
http://localhost:8000/docs

Run the complete pipeline (Spark):
.\tasks_docker.ps1 run

Stop all services:
.\tasks_docker.ps1 down

---

## Scope and Limitations

This project intentionally focuses on **core batch processing concepts** and therefore excludes:

- streaming platforms  
- cloud storage  
- workflow schedulers  
- analytics or visualization layers  

The reduced scope allows a clear and focused demonstration of fundamental batch data engineering principles.