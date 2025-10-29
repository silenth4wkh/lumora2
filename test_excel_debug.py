import requests
import time

# No Fluff Jobs scraper futtatása
print("1. No Fluff Jobs scraper futtatása...")
response = requests.post('http://localhost:5000/api/test/nofluffjobs-no-dedup', json={})
print(f"   Status: {response.status_code}")

# Várakozás a befejezésre
time.sleep(2)

# Excel export
print("\n2. Excel export...")
response = requests.get('http://localhost:5000/api/export/excel')
print(f"   Status: {response.status_code}")
print(f"   Content-Length: {len(response.content)} bytes")

# Fájl mentése
with open('nofluffjobs_debug.xlsx', 'wb') as f:
    f.write(response.content)
print("   Fájl mentve: nofluffjobs_debug.xlsx")

# Jobs API ellenőrzés
print("\n3. Jobs API ellenőrzése...")
response = requests.get('http://localhost:5000/api/jobs')
data = response.json()
if isinstance(data, list):
    print(f"   Jobs count: {len(data)}")
    if len(data) > 0:
        print(f"   Első job mezői: {list(data[0].keys())}")
else:
    print(f"   Jobs count: {data.get('count', 0)}")
    if data.get('jobs'):
        print(f"   Első job mezői: {list(data['jobs'][0].keys())}")

print("\nKÉSZ!")

