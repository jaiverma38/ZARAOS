import argparse
import time
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="https://localhost:8443")
parser.add_argument("--token", required=True)
parser.add_argument("--device-id", default="zara-test-device")
parser.add_argument("--verify", default="false")
args = parser.parse_args()
verify = args.verify.lower() not in {"0", "false", "no"}
headers = {"Authorization": f"Bearer {args.token}"}

def envelope(payload):
    return {"protocol": "zaraos.ai.v1", "device_id": args.device_id, "correlation_id": str(time.time_ns()), "locale": "hi-IN", "timestamp_ms": int(time.time() * 1000), "payload": payload}

for path, payload in [
    ("/v1/health", {}),
    ("/v1/llm/intent", {"text": "Zara mere paas aao"}),
    ("/v1/llm/chat", {"text": "Namaste Zara"}),
]:
    response = requests.post(args.base_url + path, json=envelope(payload), headers=headers, timeout=120, verify=verify)
    response.raise_for_status()
    print(path, response.json())
