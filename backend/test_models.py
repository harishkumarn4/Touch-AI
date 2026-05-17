import requests
import json

api_key = "AIzaSyDBVsyJKnthtaqE2cKS2zM_xvJQYBp8Zu0"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print(json.dumps(response.json(), indent=2))
