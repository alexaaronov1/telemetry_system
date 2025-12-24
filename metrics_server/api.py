"""
REST API for serving aggregated telemetry metrics.
"""

import time
import os
import json
import logging
from flask import Flask, request, jsonify
from .storage import TelemetryStorage
from .ingestion import start_ingestion

DEFAULT_LOG_LEVEL = "INFO"

# -----------------------
# Configuration loading
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        logging.warning("Config file not found, using defaults")
        return {
            "logging": {"level": DEFAULT_LOG_LEVEL}
        }

    with open(CONFIG_PATH) as f:
        return json.load(f)


def configure_logging(level_str):
    level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    logging.info("Logging level set to %s", level_str)


config = load_config()
configure_logging(config.get("logging", {}).get("level", DEFAULT_LOG_LEVEL))


# -----------------------
# Flask app
# -----------------------
METRICS_SERVER_HOST = os.getenv("METRICS_SERVER_HOST", "127.0.0.1")
METRICS_SERVER_PORT = int(os.getenv("METRICS_SERVER_PORT", 8080))

app = Flask(__name__)

# create the storage
storage = TelemetryStorage()

# start the ingestion
GENERATOR_HOST = os.getenv("GENERATOR_HOST", "127.0.0.1")
GENERATOR_PORT = int(os.getenv("GENERATOR_PORT", 9001))
SOURCE = f"http://{GENERATOR_HOST}:{GENERATOR_PORT}/counters"
start_ingestion(storage, SOURCE)

# hooks to measure and log end-to-end API latency
@app.before_request
def start_timer():
    request._start_time = time.perf_counter()

@app.after_request
def log_latency(response):
    duration = (time.perf_counter() - request._start_time) * 1000
    logging.info("%s %d %.2fms", request.path, response.status_code, duration)
    return response

# -----------------------
# API endpoints
# -----------------------

@app.route("/telemetry/GetMetric")
def get_metric():
    sw = request.args.get("switch")
    metric = request.args.get("metric")

    snapshot = storage.snapshot()

    if not sw or not metric:
        return jsonify(error="missing parameters"), 400
    if sw not in snapshot:
        return jsonify(error="switch not found"), 404
    if metric not in snapshot[sw]:
        return jsonify(error="metric not found"), 404

    return jsonify(
        switch=sw,
        metric=metric,
        value=snapshot[sw][metric],
        timestamp=snapshot[sw]["timestamp"]
    )

@app.route("/telemetry/ListMetrics")
def list_metrics():
   return jsonify(storage.snapshot())

if __name__ == "__main__":
    app.run(host=METRICS_SERVER_HOST, port=METRICS_SERVER_PORT)
