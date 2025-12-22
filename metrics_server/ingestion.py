import csv
import io
import time
import requests
import threading

def ingest_loop(storage, url):
    while True:
        try:
            resp = requests.get(url, timeout=2)
            reader = csv.DictReader(io.StringIO(resp.text))
            parsed = {}
            for row in reader:
                sw = row.pop("switch_id")
                parsed[sw] = {k: float(v) for k, v in row.items()}
            storage.update(parsed)
        except Exception as e:
            print(f"[ingestion] error: {e}")
        time.sleep(10)

def start_ingestion(storage, url):
    t = threading.Thread(target=ingest_loop, args=(storage, url), daemon=True)
    t.start()
