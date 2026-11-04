#!/usr/bin/env python3
"""Save the Make review form: API doc link + one scenario URL per module + error scenario.

Usage: MAKE_ZONE=us2 python3 scripts/review_form.py scenarios.json
where scenarios.json is {"errorHandlingScenario": url, "testingScenarios": {moduleName: url}}.
Token: MAKE_TOKEN or .secrets/make-apikey. App name from make/.deploy-state.json.
"""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
zone = os.environ.get("MAKE_ZONE", "us2")
tok = os.environ.get("MAKE_TOKEN") or open(os.path.join(ROOT, ".secrets", "make-apikey")).read().strip()
app = json.load(open(os.path.join(ROOT, "make", ".deploy-state.json")))["appName"]
body = json.load(open(sys.argv[1])); body.setdefault("apiDoc", "https://api.juzpost.com/docs")
req = urllib.request.Request(f"https://{zone}.make.com/api/v2/sdk/apps/{app}/1/review/form", data=json.dumps(body).encode(), method="PUT")
for k, v in {"Authorization": f"Token {tok}", "User-Agent": "juzpost-integrations-deploy/1.0", "Content-Type": "application/json"}.items():
    req.add_header(k, v)
print(urllib.request.urlopen(req).read().decode()[:400])
