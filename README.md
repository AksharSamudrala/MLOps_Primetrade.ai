# Primetrade.ai Technical Assessment

## Overview

This project implements a minimal batch processing pipeline in Python.

Features:
- Loads configuration from YAML
- Reads the given CSV data
- Computes rolling mean on the `close` column
- Generates binary trading signals
- Produces machine-readable metrics
- Generates detailed logs
- Supports Docker execution

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Local Run

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Docker

Build:

```bash
docker build -t mlops-task .
```

Run:

```bash
docker run --rm mlops-task
```

---

## Output

Example `metrics.json`

```json
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.5012,
    "latency_ms": 65,
    "seed": 42,
    "status": "success"
}
```

The exact values will vary depending on the dataset and execution environment.

---

## Files

- `run.py` – Main batch processing script
- `config.yaml` – Configuration file
- `data.csv` – Input dataset
- `requirements.txt` – Python dependencies
- `Dockerfile` – Docker build instructions
- `metrics.json` – Output metrics
- `run.log` – Execution logs
