import time
import random
import threading
from flask import Flask, Response

app = Flask(__name__)

SWITCHES = ["sw1", "sw2", "sw3", "sw4"]
METRICS = ["bandwidth_mbps", "latency_ms", "packet_errors"]

state = {}
lock = threading.Lock()

def update_metrics():
    while True:
        new_state = {}
        for sw in SWITCHES:
            latency = round(random.uniform(0.5, 2.0), 2)
            if random.random() < 0.1:
                latency *= random.randint(5, 10)

            new_state[sw] = {
                "bandwidth_mbps": random.randint(6000, 10000),
                "latency_ms": latency,
                "packet_errors": random.randint(0, 5) if random.random() < 0.1 else 0
            }

        with lock:
            state.clear()
            state.update(new_state)

        time.sleep(10)

@app.route("/counters", methods=["GET"])
def counters():
    with lock:
        rows = ["switch_id," + ",".join(METRICS)]
        for sw, metrics in state.items():
            row = [sw] + [str(metrics[m]) for m in METRICS]
            rows.append(",".join(row))
    return Response("\n".join(rows), mimetype="text/csv")

if __name__ == "__main__":
    threading.Thread(target=update_metrics, daemon=True).start()
    app.run(port=9001)
