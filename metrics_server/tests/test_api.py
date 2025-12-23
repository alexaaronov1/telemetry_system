import pytest
from ..api import app, storage


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def seed_storage():
    """
    Seed storage with deterministic data for tests.
    """
    storage._snapshot = {
        "sw1": {
            "bandwidth_mbps": 8000,
            "latency_ms": 1.5,
            "packet_errors": 0,
            "link_status": 1,
            "tx_queue_depth": 100,
            "utilization_percent": 45.0,
            "timestamp": 1234567890,
        }
    }


# -------------------------
# GetMetric tests
# -------------------------

def test_get_metric_success(client):
    seed_storage()
    resp = client.get(
        "/telemetry/GetMetric?switch=sw1&metric=bandwidth_mbps"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["value"] == 8000
    assert data["switch"] == "sw1"
    assert data["metric"] == "bandwidth_mbps"


def test_get_metric_missing_params(client):
    resp = client.get("/telemetry/GetMetric")
    assert resp.status_code == 400


def test_get_metric_unknown_switch(client):
    seed_storage()
    resp = client.get(
        "/telemetry/GetMetric?switch=swX&metric=bandwidth_mbps"
    )
    assert resp.status_code in (400, 404)


def test_get_metric_unknown_metric(client):
    seed_storage()
    resp = client.get(
        "/telemetry/GetMetric?switch=sw1&metric=unknown"
    )
    assert resp.status_code == 404


# -------------------------
# ListMetrics tests
# -------------------------

def test_list_metrics(client):
    seed_storage()
    resp = client.get("/telemetry/ListMetrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sw1" in data
    assert "bandwidth_mbps" in data["sw1"]
    assert "timestamp" in data["sw1"]
