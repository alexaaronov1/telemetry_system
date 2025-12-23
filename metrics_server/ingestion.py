"""
Background ingestion loop that periodically fetches telemetry data.
"""

import csv
import io
import time
import requests
import threading
import logging

INGEST_INTERVAL_SEC = 10  

def ingest_loop(storage, url):
    while True:
        try:
            ts_before_request = time.perf_counter()
            resp = requests.get(url, timeout=2) # CSV format
            duration = (time.perf_counter() - ts_before_request) * 1000
            logging.debug("[ingestion] request duration: %.2fms", duration)    
            reader = csv.DictReader(io.StringIO(resp.text))
            parsed = {}
            for row in reader:
                sw = row.pop("switch_id")
                # convert CSV strings to floats for all metrics
                parsed[sw] = {k: float(v) for k, v in row.items()}
            storage.update(parsed)
        except Exception as e:
            logging.error("[ingestion] error: %s", e)
        time.sleep(INGEST_INTERVAL_SEC)

def start_ingestion(storage, url):
    t = threading.Thread(target=ingest_loop, args=(storage, url), daemon=True)
    t.start()
