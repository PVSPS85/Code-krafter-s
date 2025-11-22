import requests
API_KEY = "AIzaSyBftZx-hhdo5TozaFqFu9S--t2GYY9_mp0"  # put your Studio API key here
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
res = requests.get(url)
print(res.status_code)
print(res.json())
