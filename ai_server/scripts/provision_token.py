import argparse
import time
import jwt

parser = argparse.ArgumentParser()
parser.add_argument("--secret", required=True)
parser.add_argument("--device-id", required=True)
parser.add_argument("--hours", type=int, default=24 * 365)
args = parser.parse_args()
now = int(time.time())
print(jwt.encode({"sub": args.device_id, "iat": now, "exp": now + args.hours * 3600}, args.secret, algorithm="HS256"))
