# Serverless-data-pipeline

Intern ID : CITS5207

## Overview
This project is a locally built simulation of an AWS-style **serverless data pipeline**. It automates the complete ETL lifecycle: fetching data from a public API, storing raw snapshots, transforming and validating the data, loading processed records into a database, logging pipeline execution, tracking ETL run history, exposing analytics through APIs, and visualizing both business metrics and pipeline health in a dashboard.

The goal of the project is to demonstrate how a modular backend/data engineering system can be designed locally while conceptually mapping to cloud-native serverless services such as **AWS Lambda, S3, EventBridge, API Gateway, and CloudWatch**.

---

## Problem Statement
Many data workflows require automated ingestion of external data, transformation into analytics-ready form, storage for downstream use, and monitoring of pipeline health. This project solves that by building an end-to-end pipeline that:

- fetches data from a public API
- stores raw and processed snapshots
- performs data cleaning and validation
- persists transformed records
- tracks ETL execution history
- exposes analytics and health endpoints
- visualizes results in a dashboard

---

## Project Goals
The pipeline is designed to:

1. Fetch data from a public API  
2. Clean and transform the data  
3. Store processed data in a database  
4. Maintain logs for monitoring and debugging  
5. Generate analytics and expose them through APIs  
6. Run automatically on a schedule  

---

## Features
- Automated ingestion from a public REST API
- Raw JSON snapshot storage
- Data cleaning and transformation using Pandas
- Derived metrics such as title length, body length, and word count
- SQLite-based storage for processed data
- Dedicated pipeline run history table for ETL observability
- Logging of ETL events and failures
- FastAPI endpoints for analytics and pipeline health
- Streamlit dashboard for KPI visualization and monitoring
- Scheduled execution using APScheduler
- Local design mapped to AWS serverless architecture

---

## Tech Stack
- **Python**
- **FastAPI**
- **Pandas**
- **SQLite**
- **Streamlit**
- **APScheduler**
- **Requests**

---

## System Architecture

### High-Level Workflow
1. A scheduler triggers the ETL job at a fixed interval.
2. The ingestion layer fetches data from a public API and stores a raw JSON snapshot.
3. The transformation layer cleans the data, removes duplicates, validates fields, and computes derived metrics.
4. A processed CSV snapshot is stored locally.
5. The storage layer inserts transformed records into SQLite.
6. ETL run metadata is saved into a `pipeline_runs` table for monitoring.
7. FastAPI exposes analytics and health endpoints.
8. Streamlit consumes those endpoints and displays analytics + pipeline health.

---

## Architecture Diagram

```text
+------------------------+
|  APScheduler Job       |
|  (Local Scheduler)     |
+-----------+------------+
            |
            v
+------------------------+
| Ingestion Layer        |
| fetch_data.py          |
| - Call public API      |
| - Save raw JSON        |
+-----------+------------+
            |
            v
+------------------------+
| Transformation Layer   |
| clean_data.py          |
| - Validate columns     |
| - Remove duplicates    |
| - Clean title/body     |
| - Add derived metrics  |
| - Save processed CSV   |
+-----------+------------+
            |
            v
+------------------------+         +---------------------------+
| Storage Layer          |         | Monitoring Layer         |
| repository.py          |         | logger.py                |
| - processed_posts      |<------->| - pipeline.log           |
| - pipeline_runs        |         | - status/error logging   |
| SQLite DB              |         +---------------------------+
+-----------+------------+
            |
            v
+------------------------+
| FastAPI API Layer      |
| main.py                |
| /metrics               |
| /posts-per-user        |
| /pipeline-health       |
| /pipeline-runs         |
+-----------+------------+
            |
            v
+------------------------+
| Streamlit Dashboard    |
| streamlit_app.py       |
| - Analytics KPIs       |
| - Pipeline health      |
| - Posts per user       |
| - Recent pipeline runs |
+------------------------+
