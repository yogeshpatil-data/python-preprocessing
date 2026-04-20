# 📦 PostgreSQL → S3 Incremental Ingestion Pipeline (Production-Grade Guide)

---

# 🔥 1. Overview

This document explains how to design a **production-grade pipeline** to extract data incrementally from PostgreSQL and store it in Amazon S3 in JSON format.

The design focuses on:

* Incremental extraction (no full table scans)
* Memory-efficient streaming
* High-throughput batch processing
* Fault tolerance and idempotency
* Scalability and observability

---

# 🔥 2. Core Pipeline Flow

```text
PostgreSQL → Incremental Query → Streaming Read → Batch Buffer → JSON Conversion → S3 Upload → State Update
```

---

# 🔥 3. Key Concepts (Very Important)

---

## 🔹 3.1 Incremental Extraction

Incremental extraction means fetching only **new or changed records** since the last successful run.
Instead of scanning the entire table repeatedly, the pipeline uses a **watermark column** (e.g., `updated_at` or `id`).
This reduces load on the database and improves efficiency significantly.
The last processed value is stored externally and reused in subsequent runs.

---

## 🔹 3.2 Watermarking

A watermark is a value that represents the **last processed position** in the dataset.
It can be a timestamp (`updated_at`) or a monotonically increasing key (`id`).
During each run, only records greater than the watermark are fetched.
Watermarking enables reliable incremental processing and avoids duplicates.

---

## 🔹 3.3 Streaming Read from PostgreSQL

Streaming ensures that data is read **row-by-row or in chunks**, instead of loading everything into memory.
This is achieved using **server-side cursors** in PostgreSQL.
Streaming is essential for handling large datasets without memory issues.
It allows the pipeline to scale efficiently to millions of rows.

---

## 🔹 3.4 Batch Processing

Batch processing groups multiple rows before writing them to S3.
This reduces the number of S3 API calls and improves throughput.
Batching balances memory usage and performance.
Typical batch sizes range from 500 to 5000 rows.

---

## 🔹 3.5 JSON Lines Format (JSONL)

JSONL stores one JSON object per line, making it ideal for streaming writes.
Each record can be written independently without building a full JSON array.
This format is widely used in data lakes and downstream processing systems.
It simplifies ingestion into systems like Spark and Snowflake.

---

## 🔹 3.6 State Management

State management involves storing the last processed watermark.
This ensures the pipeline resumes correctly after failures.
State is typically stored in a metadata table or file.
Proper state management is critical for reliable incremental pipelines.

---

## 🔹 3.7 Idempotency

Idempotency ensures that re-running the pipeline does not create duplicate data.
This is achieved by designing extraction logic based on watermarks.
Retries should not lead to duplicate file generation or inconsistent state.
Idempotent pipelines are essential for production reliability.

---

# 🔥 4. Production-Grade Script

---

```python
import psycopg2
import boto3
import json
import logging
from datetime import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------
BATCH_SIZE = 1000
S3_BUCKET = "your-bucket"
S3_PREFIX = "data/export/"
STATE_FILE = "last_watermark.txt"

# ---------------------------
# LOGGING
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# LOAD WATERMARK
# ---------------------------
def load_watermark():
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except:
        return "1970-01-01 00:00:00"

def save_watermark(value):
    with open(STATE_FILE, "w") as f:
        f.write(value)

last_watermark = load_watermark()

# ---------------------------
# DB CONNECTION
# ---------------------------
conn = psycopg2.connect(
    host="localhost",
    database="test_db",
    user="postgres",
    password="password"
)

cursor = conn.cursor(name="stream_cursor")  # server-side cursor
cursor.itersize = BATCH_SIZE

query = f"""
SELECT id, name, age, updated_at
FROM users
WHERE updated_at > '{last_watermark}'
ORDER BY updated_at ASC
"""

cursor.execute(query)

# ---------------------------
# S3 CLIENT
# ---------------------------
s3 = boto3.client("s3")

batch = []
file_count = 0
max_watermark = last_watermark

columns = [desc[0] for desc in cursor.description]

try:
    for row in cursor:
        record = dict(zip(columns, row))

        # track latest watermark
        max_watermark = record["updated_at"]

        batch.append(record)

        if len(batch) == BATCH_SIZE:
            file_count += 1
            file_name = f"{S3_PREFIX}file_{file_count}.json"

            json_data = "\n".join(json.dumps(r, default=str) for r in batch)

            s3.put_object(
                Bucket=S3_BUCKET,
                Key=file_name,
                Body=json_data
            )

            batch.clear()

    # remaining data
    if batch:
        file_count += 1
        file_name = f"{S3_PREFIX}file_{file_count}.json"

        json_data = "\n".join(json.dumps(r, default=str) for r in batch)

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=file_name,
            Body=json_data
        )

    # update watermark
    save_watermark(str(max_watermark))

    logger.info("Incremental extraction completed successfully")

except Exception as e:
    logger.error(f"Error occurred: {str(e)}")

finally:
    cursor.close()
    conn.close()
```

---

# 🔥 5. Why This Design Works

---

## ✔ Efficient Incremental Reads

Only new data is fetched using watermark filtering.

## ✔ Memory Efficient

Streaming avoids loading full datasets into memory.

## ✔ High Throughput

Batch writes reduce S3 API overhead.

## ✔ Fault Tolerant

Watermark ensures recovery after failure.

---

# 🔥 6. Real-World Enhancements (DETAILED)

---

## 🔹 6.1 Key-Based Pagination (Better than OFFSET)

### Concept

OFFSET-based pagination becomes slow for large tables because the database scans skipped rows.
Key-based pagination uses a column like `id` or `timestamp` to fetch the next batch efficiently.
This approach scales much better for large datasets.
It is the preferred method in production systems.

### Example

```sql
SELECT * FROM users
WHERE id > last_id
ORDER BY id
LIMIT 1000;
```

---

## 🔹 6.2 Parallel Extraction

### Concept

Large tables can be split into partitions and processed in parallel.
This improves throughput and reduces total execution time.
Partitioning can be done using ID ranges or timestamps.
Parallel extraction is critical for large-scale pipelines.

### Example

```python
# process id ranges in parallel
# id 1–10000, 10001–20000, etc.
```

---

## 🔹 6.3 Compression Before Upload

### Concept

Compressing data before uploading reduces storage and network cost.
Gzip is commonly used in data pipelines.
Compression also improves downstream processing performance.
It is a standard practice in production systems.

### Example

```python
import gzip

compressed = gzip.compress(json_data.encode())

s3.put_object(Bucket=S3_BUCKET, Key=file_name + ".gz", Body=compressed)
```

---

## 🔹 6.4 Partitioned S3 Layout

### Concept

Partitioning organizes data into directories based on attributes like date.
This improves data discovery and incremental processing.
Partitioning is a core concept in data lakes.
It enables efficient downstream querying.

### Example

```text
s3://bucket/data/date=2026-04-20/file.json
```

---

## 🔹 6.5 Retry Mechanism

### Concept

Failures can occur due to network issues or service limits.
Retry logic ensures temporary failures do not break the pipeline.
Exponential backoff prevents overwhelming systems.
Retries improve reliability and robustness.

### Example

```python
import time

def retry(func):
    for i in range(3):
        try:
            return func()
        except:
            time.sleep(2 ** i)
```

---

## 🔹 6.6 Connection Pooling

### Concept

Reusing database connections reduces overhead.
Connection pooling improves performance and scalability.
It is essential for high-throughput systems.
Pooling prevents frequent connection creation.

---

## 🔹 6.7 Logging & Monitoring

### Concept

Logging provides visibility into pipeline execution.
Monitoring tracks performance metrics and failures.
This is essential for debugging and production operations.
Observability ensures reliability and maintainability.

---

## 🔹 6.8 Schema Evolution Handling

### Concept

Schemas can change over time in real-world systems.
Pipelines should handle new or missing fields gracefully.
Flexible parsing and validation help maintain stability.
Schema evolution is critical in long-running pipelines.

---

# 🔥 7. Final Architecture

```text
PostgreSQL (incremental query)
    ↓
Streaming Cursor
    ↓
Batch Processing
    ↓
JSONL Conversion
    ↓
S3 (partitioned, compressed)
    ↓
State Store (watermark)
```

---

# 🔥 8. Interview Summary

> A production-grade incremental pipeline from PostgreSQL to S3 should use watermark-based extraction, streaming reads, batch processing, and JSONL output. It should also implement state management, partitioning, compression, retries, and monitoring to ensure scalability and reliability.

---

# 🔥 Final Mental Model

```text
Query new data → stream → batch → write → update watermark → repeat
```

---

**End of Document**
