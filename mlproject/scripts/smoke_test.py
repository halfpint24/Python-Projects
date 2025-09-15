
#!/usr/bin/env python3
"""
Simple smoke test for the Iris API.
Run the API (e.g., docker run -p 8000:8000 ...), then execute:
    python scripts/smoke_test.py
"""
import json
import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:8000'

def get(url):
    with urllib.request.urlopen(url) as resp:
        return resp.getcode(), json.loads(resp.read().decode('utf-8'))

def post(url, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        # Return status + parsed error body if available
        try:
            body = e.read().decode('utf-8')
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'detail': body if body else str(e)}

def main():
    print('== Health check ==')
    code, body = get(BASE + '/healthz')
    print(code, body)

    print('\n== Valid input ==')
    code, body = post(BASE + '/predict', {'features': [5.1, 3.5, 1.4, 0.2]})
    print(code, body)

    print('\n== Invalid length (3 values) ==')
    code, body = post(BASE + '/predict', {'features': [5.1, 3.5, 1.4]})
    print(code, body)

    print('\n== Wrong type (string) ==')
    code, body = post(BASE + '/predict', {'features': [5.1, 'oops', 1.4, 0.2]})
    print(code, body)

    print('\n== Boundary too large (99) ==')
    code, body = post(BASE + '/predict', {'features': [5.1, 3.5, 99, 0.2]})
    print(code, body)

    print('\n== Negative value ==')
    code, body = post(BASE + '/predict', {'features': [-1.0, 3.5, 1.4, 0.2]})
    print(code, body)

if __name__ == '__main__':
    main()
