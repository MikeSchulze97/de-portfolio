# Data Engineering Portfolio – Batch Event Pipeline

This project was created as part of the **Data Engineering portfolio assessment** at IU.

It demonstrates a **batch-based data pipeline**, covering the full flow from data ingestion to batch processing and aggregation.

The project focuses on deterministic data processing, clear data flow, and reproducible execution using Docker and Apache Spark.

---

## Project Overview

The pipeline implements a batch-oriented architecture that:

- receives events via an HTTP API  
- stores raw events unchanged  
- processes events in batch jobs  
- aggregates results per time window  
- can be executed repeatedly with consistent results  

---

## Pipeline Structure

The pipeline consists of the following components:

### Ingestion Service
- A FastAPI service that receives events via HTTP  
- Each incoming event is stored as a raw JSON file  
- No transformation is applied at ingestion time  

### Batch Processing (Spark)
- Reads raw event files  
- Extracts event time from filenames  
- Validates and structures the data  
- Writes processed events into time-based partitions  

### Aggregation (Spark)
- Reads processed data per partition  
- Aggregates events by event type  
- Writes aggregated results as JSON files  

All components are executed using **Docker and Docker Compose**.

---

## Architecture

The data flows through the system as follows:

Event Generator (optional)  
→ Ingestion Service (FastAPI)  
→ Raw data storage  
→ Batch Processing (Spark)  
→ Processed data (partitioned by date and hour)  
→ Aggregation (Spark)  
→ Aggregated result files  

All data is stored locally on the filesystem to allow full inspection of each processing stage.

---

## Data Handling

### Raw Data
- Each event is stored as a single JSON file  
- Event time is encoded in the filename  
- Raw data is never modified after ingestion  

### Processed Data
- Valid events are written to partitioned directories:
  - `date=YYYY-MM-DD/hour=HH`
- Partitioning is based on event time  

### Aggregated Data
- Events are counted per partition and event type  
- Results are written to `event_counts.json`  

---

## Checkpoints and Reproducibility

The pipeline uses checkpoint files to track processing state.

This ensures that:
- already processed data is not duplicated  
- batch jobs can be re-run safely  
- execution remains deterministic across runs  

---

## Directory Structure (Simplified)

data/
├── raw/
├── processed/
│   └── date=YYYY-MM-DD/
│       └── hour=HH/
├── aggregated/
│   └── date=YYYY-MM-DD/
│       └── hour=HH/
└── _checkpoints/

Generated data directories are excluded from version control.

---

## Running the Pipeline

All commands are executed via a PowerShell helper script.

Start the ingestion service:
.\tasks_docker.ps1 up

(Optional) Run the event generator (requires a CSV file):
.\tasks_docker.ps1 generator

Run the complete pipeline (Spark):
.\tasks_docker.ps1 run

Stop all services:
.\tasks_docker.ps1 down

Access API documentation:
http://localhost:8000/docs

---

## Scope and Limitations

The project focuses on batch data processing and does not include:

- streaming platforms  
- cloud storage  
- workflow schedulers  
- analytics or visualization layers  
