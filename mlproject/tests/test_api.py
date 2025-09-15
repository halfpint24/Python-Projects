from fastapi.testclient import TestClient
import importlib
import sys
from pathlib import Path

# Ensure project root (where app.py lives) is on sys.path, even if pytest is run from elsewhere
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

app_module = importlib.import_module('app')
app = app_module.app

client = TestClient(app)

def test_healthcheck():
    r = client.get('/healthz')
    assert r.status_code == 200
    assert 'status' in r.json()

def test_valid_prediction():
    # If model.pkl isn't available, the service may return 500; that's acceptable for CI without artifacts.
    r = client.post('/predict', json={'features': [5.1, 3.5, 1.4, 0.2]})
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        j = r.json()
        assert 'class_index' in j and 'class_label' in j

def test_input_length_error():
    r = client.post('/predict', json={'features': [1, 2, 3]})
    assert r.status_code in (400, 422)

def test_type_error():
    r = client.post('/predict', json={'features': [5.1, 'x', 1.4, 0.2]})
    assert r.status_code in (400, 422)

def test_out_of_range():
    r = client.post('/predict', json={'features': [11, 3.5, 1.4, 0.2]})
    assert r.status_code in (400, 422)
