import urllib.request
import time

urls = [
    "http://127.0.0.1:5000/",
    "http://127.0.0.1:5000/map",
    "http://127.0.0.1:5000/analytics",
    "http://127.0.0.1:5000/api/stats"
]

for i in range(5):
    for url in urls:
        try:
            print(f"Fetching {url}... ", end="")
            with urllib.request.urlopen(url) as resp:
                print(f"Status: {resp.status}")
        except Exception as e:
            print(f"Error: {e}")
    time.sleep(1)
