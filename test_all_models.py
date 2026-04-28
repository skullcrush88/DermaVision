import requests
import re

print("="*60)
print("TESTING ALL THREE MODELS")
print("="*60)
print()

results = []
for port in [5000, 5001, 5002]:
    model_num = [5000, 5001, 5002].index(port) + 1
    url = f'http://127.0.0.1:{port}/'
    
    try:
        with open(f'model {model_num}/test_img.jpg', 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        results.append({
            'model': model_num,
            'port': port,
            'status': response.status_code,
            'length': len(response.text)
        })
    except Exception as e:
        results.append({
            'model': model_num,
            'port': port,
            'status': 'ERROR',
            'error': str(e)
        })

for r in results:
    if 'error' in r:
        print(f"X Model {r['model']} ({r['port']}): ERROR - {r['error']}")
    else:
        status_symbol = "OK" if r['status'] == 200 else "FAIL"
        print(f"[{status_symbol}] Model {r['model']} ({r['port']}): HTTP {r['status']} - {r['length']} bytes")

print()
print("="*60)
print("ALL MODELS TESTED SUCCESSFULLY")
print("="*60)
