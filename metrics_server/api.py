import time
from flask import Flask, request, jsonify
from storage import TelemetryStorage
from ingestion import start_ingestion

app = Flask(__name__)
storage = TelemetryStorage()

SOURCE = "http://127.0.0.1:9001/counters"
start_ingestion(storage, SOURCE)

@app.before_request
def start_timer():
    request._start_time = time.time()

@app.after_request
def log_latency(response):
    duration = (time.time() - request._start_time) * 1000
    print(f"{request.path} {response.status_code} {duration:.2f}ms")
    return response

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
    app.run(port=8080)
