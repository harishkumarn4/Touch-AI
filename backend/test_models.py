import os
import requests
import json
import sys

# Prefer reading the key from an environment variable for safety
api_key = os.environ.get("GOOGLE_API_KEY") or "AIzaSyAUNzM_vJRwWS8Cw9LBWlOMkNGOuCd138Q"

def _mask_key(k: str) -> str:
	if not k:
		return "<empty>"
	if len(k) <= 8:
		return k
	return k[:4] + "..." + k[-4:]

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
	resp = requests.get(url, timeout=10)
	print("API key (masked):", _mask_key(api_key))
	print("Status code:", resp.status_code)
	try:
		print(json.dumps(resp.json(), indent=2))
	except ValueError:
		print("Response text:", resp.text)
		sys.exit(1)
except requests.RequestException as e:
	print("Request failed:", e)
	sys.exit(1)
