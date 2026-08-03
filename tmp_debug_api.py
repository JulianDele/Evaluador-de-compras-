import json
import urllib.request
import urllib.error

url = 'http://localhost:8000/api/v1/auth/login'
data = {'email': 'admin@consumo.local', 'password': 'Consumo2024!'}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode('utf-8')
        print('LOGIN', resp.status)
        print(body)
except urllib.error.HTTPError as exc:
    body = exc.read().decode('utf-8', errors='ignore')
    print('HTTPError', exc.code)
    print(body)
except Exception as exc:
    print(type(exc).__name__, exc)
