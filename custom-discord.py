#!/usr/bin/env python3
import sys
import json
import requests

"""
ossec.conf configuration structure
 <integration>
     <name>custom-discord</name>
     <hook_url>https://discord.com/api/webhooks/XXXXXXXXXXX</hook_url>
     <alert_format>json</alert_format>
 </integration>
"""

# Validate argument count before touching sys.argv
if len(sys.argv) < 4:
    print("Usage: custom-discord.py <alert_file> <user> <hook_url>", file=sys.stderr)
    sys.exit(1)

# Read configuration (user/argv[2] intentionally unused — kept for Wazuh compat)
alert_file = sys.argv[1]
hook_url = sys.argv[3]

# Read and parse alert file
try:
    with open(alert_file) as f:
        alert_json = json.loads(f.read())
except OSError as e:
    print(f"ERROR: Could not open alert file '{alert_file}': {e}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse alert JSON: {e}", file=sys.stderr)
    sys.exit(1)

# Extract alert level — required field, hard fail if missing
try:
    alert_level = alert_json["rule"]["level"]
except KeyError as e:
    print(f"ERROR: Missing required field in alert JSON: {e}", file=sys.stderr)
    sys.exit(1)

# Colors from https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
# Discord requires color as an integer, not a string
if alert_level < 5:
    color = 5763719       # green
elif alert_level <= 7:
    color = 16705372      # yellow
else:
    color = 15548997      # red

# Agent details — fall back gracefully for agentless alerts
if "agentless" in alert_json:
    agent_ = "agentless"
else:
    agent_ = alert_json.get("agent", {}).get("name", "unknown")

# Build payload — catch any remaining missing fields here
try:
    payload = json.dumps({
        "content": "",
        "embeds": [
            {
                "title": f"Wazuh Alert - Rule {alert_json['rule']['id']}",
                "color": color,
                "description": alert_json["rule"]["description"],
                "fields": [{
                    "name": "Agent",
                    "value": agent_,
                    "inline": True
                }]
            }
        ]
    })
except KeyError as e:
    print(f"ERROR: Missing field when building Discord payload: {e}", file=sys.stderr)
    sys.exit(1)

# Send message to Discord with a timeout and HTTP error check
try:
    r = requests.post(
        hook_url,
        data=payload,
        headers={"content-type": "application/json"},
        timeout=10
    )
    r.raise_for_status()
except requests.exceptions.Timeout:
    print("ERROR: Request to Discord timed out after 10s", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.HTTPError as e:
    print(f"ERROR: Discord returned HTTP error: {e}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"ERROR: Failed to reach Discord: {e}", file=sys.stderr)
    sys.exit(1)

sys.exit(0)