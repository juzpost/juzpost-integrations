#!/usr/bin/env python3
"""Generate Make scenario blueprints for the review test run.

Usage: python3 scripts/gen_make_test_scenarios.py <connectionId> [appName]
Writes make/test-scenarios/*.json. Import each in Make: scenario editor, "..." menu,
Import Blueprint. Nothing here publishes: Schedule a Post only appears in the error
scenario with a fake account id and a date in the past, and Smart Schedule runs dry.
"""
import json, os, sys

CONN = int(sys.argv[1])
APP = sys.argv[2] if len(sys.argv) > 2 else "juzpost-k2gkrv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "make", "test-scenarios")
os.makedirs(OUT, exist_ok=True)


def mod(i, name, mapper=None, params=None, x=None):
    return {
        "id": i, "module": f"app#{APP}:{name}", "version": 1,
        "parameters": {"__IMTCONN__": CONN, **(params or {})},
        "mapper": mapper or {},
        "metadata": {"designer": {"x": (x if x is not None else (i - 1) * 300), "y": 0},
                     "restore": {"parameters": {"__IMTCONN__": {"data": {"scoped": "true", "connection": f"app#{APP}"},
                                                                "label": "Jeeva's JuzPost API key connection"}}},
                     "parameters": [{"name": "__IMTCONN__", "type": f"account:app#{APP}", "label": "Connection", "required": True}]},
    }


def http_get_file(i):
    return {
        "id": i, "module": "http:ActionGetFile", "version": 3,
        "parameters": {"handleErrors": False},
        "mapper": {"url": "https://cdn.juzpost.com/brand/icon.png", "method": "get", "headers": [], "qs": [],
                   "serializeUrl": False, "shareCookies": False, "timeout": "", "useMtls": False,
                   "followRedirect": True, "followAllRedirects": False, "rejectUnauthorized": True},
        "metadata": {"designer": {"x": (i - 1) * 300, "y": 0}},
    }


def scenario(name, flow):
    return {
        "name": name, "flow": flow,
        "metadata": {"instant": False, "version": 1,
                     "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True, "autoCommitTriggerLast": True,
                                  "sequential": False, "slots": None, "confidential": False, "dataloss": False,
                                  "dlq": False, "freshVariables": False},
                     "designer": {"orphans": []}, "zone": "us2.make.com"},
    }


S = {}
S["1-drafts"] = scenario("JuzPost test 1: drafts and media (no publishing)", [
    mod(1, "getMyAccount"),
    mod(2, "listAccounts", {"limit": "1"}),
    http_get_file(3),
    mod(4, "uploadMedia", {"fileName": "make-test-icon.png", "data": "{{3.data}}", "contentType": "image/png"}),
    mod(5, "createPost", {"content": "Make integration test draft. Never scheduled.", "type": "image",
                          "mediaKeys": ["{{4.mediaKey}}"], "title": "Make test", "hashtags": ["make", "test"]}),
    mod(6, "getPost", {"postId": "{{5.id}}"}),
    mod(7, "updatePost", {"postId": "{{5.id}}", "content": "Make integration test draft, updated."}),
    mod(8, "smartSchedule", {"minPerDay": 1, "socialAccountIds": ["{{2.id}}"], "postIds": ["{{5.id}}"],
                             "times": ["09:00"], "dryRun": True}),
    mod(9, "deletePost", {"postId": "{{5.id}}"}),
    mod(10, "makeApiCall", {"url": "/workspace", "method": "GET",
                            "headers": [{"key": "Content-Type", "value": "application/json"}], "qs": []}),
    mod(11, "listPosts", {"limit": "3"}),
])
S["2-accounts"] = scenario("JuzPost test 2: list accounts (pagination)", [
    mod(1, "listAccounts", {"limit": "200"}),
])
S["3-groups"] = scenario("JuzPost test 3: groups", [
    mod(1, "listGroups", {"limit": "5"}),
    mod(2, "getGroup", {"groupId": "{{1.id}}"}),
])
S["4-watch"] = scenario("JuzPost test 4: watch posts", [
    mod(1, "watchPosts", params={"status": "draft", "limit": 10}),
])
S["5-error"] = scenario("JuzPost test 5: API error handling", [
    mod(1, "createPost", {"content": "Make error-handling test draft.", "type": "text"}),
    mod(2, "schedulePost", {"postId": "{{1.id}}", "socialAccountIds": ["00000000-0000-4000-8000-000000000000"],
                            "publishAt": "2020-01-01T00:00:00.000Z"}),
])

for k, v in S.items():
    p = os.path.join(OUT, f"{k}.json")
    json.dump(v, open(p, "w"), indent=2)
    print(p)
