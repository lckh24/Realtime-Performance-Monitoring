# Real-Time Performance Monitoring

## Table of Contents
1. [Project Overview](#project-overview)
3. [Technologies Used](#technologies-used)
4. [Data Pipeline](#data-pipeline)
5. [Repository Structure](#repository-structure)
6. [Dashboard](#dashboard)
7. [Acknowledgments](#acknowledgments)
8. [Conclusion](#conclusion)
9. [Contacts](#contacts)

## Project Overview  
This project implements a real-time data pipeline using Apache Kafka, Python's psutil library for metric collection, and PostgreSQL for data storage. It collects host metrics (CPU, memory, interrupts, network I/O, disk usage) via psutil, streams them through Kafka, and stores them in PostgreSQL using SQLAlchemy. A materialized view aggregates metrics over 5-minute windows, refreshed by Airflow. Grafana provides a real-time dashboard with threshold-based alerts for monitoring.

## Technologies Used
- **FastAPI**: Develop internal APIs to expose data endpoints consumed by Airflow DAGs.  
- **Python**: Utilized the psutil library for collecting metrics data and Kafka Python client for producing and consuming messages.  
- **Airflow**: Orchestrated workflows that fetch metrics via FastAPI, process streaming data from Kafka.  
- **Apache Kafka:** Implemented a distributed streaming platform to handle real-time data processing and communication between producers and consumers.  
- **Apache Zookeeper:** Used for coordinating and managing Kafka brokers.  
- **Control Center**: Provided UI dashboard to monitor the data flow between producers, topics, and consumers.  
- **Postgres**: Stored and managed the collected metrics data in a relational database.  
- **Grafana**: Connected to the Postgres database to visualize real-time metrics and create the dashboard.  
- **Slack Webhook**: Sent Airflow logs and Grafana alerts to Slack for real-time monitoring and incident response.

## Data Pipelines    
![image](https://github.com/user-attachments/assets/ed001f5b-0b9b-4fa8-b78a-93f0c3979d89)

The data pipeline is structured as follows:  
1. **Data Ingestion**  
   - Metrics are collected on the local host via a FastAPI endpoint using the `psutil` library.  

2. **Data Production**  
   - The FastAPI service serializes each metric snapshot as JSON and publishes it into the Kafka topic `Tracking` using Python’s `kafka-python` client.  

3. **Bronze Layer (Raw Storage)**  
   - A Python Kafka consumer (built with SQLAlchemy) reads from `Tracking` and writes every raw JSON record into the `bronze.bronze_performance` table in PostgreSQL.  

4. **Silver Layer (Cleansing & Normalization)**  
   - Immediately after insertion, a transform routine filters out any records with null or out-of-range values, normalizes percentages (e.g. divides “cpu_usage” by 100), converts bytes fields as needed, and writes the cleaned data into `silver.silver_performance`.  

5. **Gold Layer (Aggregation)**  
   - A materialized view `gold.mv_perf_5min_summary` aggregates the silver data into 5-minute windows, computing:  
     - average, max, and 95th-percentile for CPU & memory  
     - total bytes sent/received  
     - anomaly flags when metrics exceed predefined thresholds  

6. **Orchestration & Alerting**  
   - An Airflow DAG runs every 30 minutes to refresh materialized.  
   - The DAG is configured with email and Slack alerts on failure or SLA miss to ensure pipeline health.  

7. **Visualization & Monitoring**  
   - Grafana connects to the PostgreSQL data source, queries the `silver_performance` table for sub-minute panels and the gold materialized view for 5-minute summaries, and renders live time-series dashboards (CPU, memory, network I/O, disk) with threshold-based alerting.  

## Repository Structures:  
``` bash
.
├── Dockerfile
├── app
│   └── main.py
├── data
│   └── airflow
│       ├── config
│       ├── data
│       └── plugins
├── docker-compose.yaml
├── load_dataset_into_postgres
├── pipeline
│   └── dags
│       ├── pipelines.py
│       └── test.py
├── requirements.txt
└── scripts
    └── pj
        ├── __init__.py
        ├── consumer.py
        ├── monitor.py
        └── producer.py
```

## Dashboard: 
![image](https://github.com/user-attachments/assets/3afdf07f-aa99-48d6-9b28-516d81eed06a)

## Conclusion:
A seamless real‐time pipeline that captures every CPU, memory, network, and disk metric, cleans and normalizes it through Bronze→Silver tables, and then rolls up 5-minute aggregates in a Gold materialized view. Airflow quietly refreshes the view on schedule, Kafka guarantees no data loss, and Grafana brings it all to life with live charts and alerts the moment anything crosses my thresholds. It’s an end-to-end solution I can trust today and extend tomorrow as my infrastructure grows.  

## Contacts:  
For any informations, please contact:  
* Email: [lecongkhanh242003@gmail.com]()  
* LinkedIn: [Here](https://www.linkedin.com/in/khanh-le-469818288/)



