# Network Telemetry Aggregation System

## Overview
This project implements a simplified network telemetry aggregation system inspired by NVIDIA UFM.
It simulates telemetry ingestion from fabric switches, stores the latest metrics in memory, and
exposes them via a REST API for real-time querying.

The system prioritizes:
- Low-latency reads
- Data freshness
- Non-blocking API access
- Clear separation between ingestion, storage, and serving layers

---

## Architecture

+-----------------------------+
| Telemetry Generator         |
| telemetry_generator/server.py|
|  REST: GET /counters        |
|  Port: 9001                 |
+-----------------------------+

               |
               |  HTTP GET (CSV)
               |
               v

+-----------------------------+
| Telemetry Aggregator        |
| metrics_server/ingestion.py |
| metrics_server/storage.py   |
|                             |
| - Pulls CSV periodically    |
| - Parses data               |
| - Updates snapshot          |
+-----------------------------+

               |
               |  In-memory read
               |
               v

+-----------------------------+
| Metrics API Server          |
| metrics_server/api.py       |
|  REST: /telemetry/*         |
|  Port: 8080                 |
+-----------------------------+


### Components
1. **Telemetry Generator**
   - Simulates switches producing telemetry metrics
   - Exposes metrics as CSV over HTTP

2. **Telemetry Aggregator**
   - Periodically pulls telemetry data
   - Stores the latest snapshot in memory

3. **Metrics API Server**
   - Serves real-time telemetry queries
   - Never performs I/O during request handling

---

## Telemetry Generator

- Runs on port `9001`
- Endpoint: `GET /counters`
- Returns a CSV matrix of switches × metrics
- Metrics are updated every 10 seconds
- Simulates realistic behavior:
  - Random bandwidth
  - Latency spikes
  - Packet error bursts

---

## Data Storage Model

Telemetry is stored as an in-memory snapshot:

```python
{
  "sw1": {
    "bandwidth_mbps": 8300,
    "latency_ms": 1.3,
    "packet_errors": 0,
    "timestamp": 1700000000
  }
}

## Running the system

1. Start the telemetry generator:
   python telemetry_generator/server.py

2. Start the metrics API server:
   python metrics_server/api.py

## Testing

The system was tested manually along the happy path:

- Verified telemetry generator produces valid CSV
- Verified ingestion loop updates in-memory snapshot
- Verified API returns correct metrics and remains responsive
- Verified API continues serving data if telemetry source becomes unavailable
