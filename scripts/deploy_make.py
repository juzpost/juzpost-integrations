#!/usr/bin/env python3
"""Deploy make/ to Make through the SDK Apps API, without the VS Code extension.

Usage:
    python3 scripts/deploy_make.py            # create or update the app
    python3 scripts/deploy_make.py --dry-run  # print the plan, send nothing

Config (environment, with defaults):
    MAKE_ZONE      eu1 | eu2 | us1 | us2 ...      default eu2
    MAKE_TOKEN     API token; or put it in .secrets/make-apikey (gitignored)
    MAKE_APP_NAME  app identifier in Make           default juzpost
    MAKE_APP_VER   app major version                default 1

The token needs the sdk-apps:read and sdk-apps:write scopes (Make: avatar, Profile, API, Add token).

Idempotent: creating something that already exists falls back to updating it. The connection
name Make assigns (it may differ from the local id) is written to make/.deploy-state.json
and every module and RPC is pointed at it.
"""
import argparse, json, os, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(HERE, "..", "make")
ROOT = os.path.join(HERE, "..")
TYPE_ID = {"trigger": 1, "action": 4, "search": 9, "instant_trigger": 10, "responder": 11, "universal": 12}
SECTION_FOR = {"communication": "api", "staticParams": "parameters", "mappableParams": "expect",
               "interface": "interface", "samples": "samples", "scope": "scope"}


def token():
    t = os.environ.get("MAKE_TOKEN")
    if t:
        return t.strip()
    p = os.path.join(ROOT, ".secrets", "make-apikey")
    if os.path.exists(p):
        return open(p).read().strip()
    sys.exit("No token. Set MAKE_TOKEN or create .secrets/make-apikey")


class Make:
    def __init__(self, zone, tok, dry):
        self.base = f"https://{zone}.make.com/api/v2"
        self.tok = tok
        self.dry = dry

    def call(self, method, path, body=None, ctype="application/json", ok404=False):
        url = self.base + path
        data = None
        if body is not None:
            data = body if isinstance(body, bytes) else (body if isinstance(body, str) else json.dumps(body)).encode()
        print(f"  {method} {path}")
        if self.dry:
            return {}
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Token {self.tok}")
        req.add_header("User-Agent", "juzpost-integrations-deploy/1.0")
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", ctype)
        try:
            with urllib.request.urlopen(req) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt.startswith(("{", "[")) else {"raw": txt}
        except urllib.error.HTTPError as e:
            txt = e.read().decode()
            if ok404 and (e.code == 404 or (e.code == 403 and "not found" in txt.lower())):
                return None
            raise SystemExit(f"{method} {path} -> HTTP {e.code}: {txt[:500]}")


def read(rel):
    with open(os.path.join(APP_DIR, rel)) as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    zone = os.environ.get("MAKE_ZONE", "eu2")
    manifest = json.load(open(os.path.join(APP_DIR, "makecomapp.json")))
    state_path = os.path.join(APP_DIR, ".deploy-state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    # Make appends a random suffix to the app name it assigns; the state file remembers it.
    name = os.environ.get("MAKE_APP_NAME") or state.get("appName") or "juzpost"
    ver = int(os.environ.get("MAKE_APP_VER", "1"))
    m = Make(zone, "dry" if a.dry_run else token(), a.dry_run)

    print(f"App {name} v{ver} on {zone}")
    app = m.call("GET", f"/sdk/apps/{name}/{ver}", ok404=True)
    if app is None:
        print("Creating app")
        r = m.call("POST", "/sdk/apps", {
            "name": name, "label": "JuzPost", "version": ver,
            "description": "Schedule and publish social media posts to 11 platforms from one calendar.",
            "theme": "#7C3AED", "language": "en", "countries": [], "beta": False, "public": False})
        if not m.dry:
            name = (r.get("app") or r).get("name", name)
            state["appName"] = name
            json.dump(state, open(state_path, "w"), indent=2)
            print(f"Make assigned the app name {name}")
    if not m.dry:
        m.call("PATCH", f"/sdk/apps/{name}/{ver}", {"theme": "#7C3AED", "description": "Schedule and publish social media posts to 11 platforms from one calendar."})

    g = manifest["generalCodeFiles"]
    print("Base, readme, groups, icon")
    m.call("PUT", f"/sdk/apps/{name}/{ver}/base", read(g["base"]), "application/jsonc")
    m.call("PUT", f"/sdk/apps/{name}/{ver}/readme", read(g["readme"]), "text/markdown")
    icon = os.path.join(ROOT, "assets", "juzpost-make-logo.png")
    if os.path.exists(icon):
        m.call("PUT", f"/sdk/apps/{name}/{ver}/icon", open(icon, "rb").read(), "image/png")

    # Connections: Make assigns the name; remember it so modules can reference it.
    conn_names = state.setdefault("connections", {})
    for local, c in manifest["components"]["connection"].items():
        if local not in conn_names:
            print(f"Creating connection {local}")
            r = m.call("POST", f"/sdk/apps/{name}/connections", {"type": c["connectionType"], "label": c["label"]})
            if m.dry:
                continue
            conn_names[local] = (r.get("appConnection") or r).get("name", local)
            json.dump(state, open(state_path, "w"), indent=2)
        remote = conn_names[local]
        cf = c["codeFiles"]
        m.call("PUT", f"/sdk/apps/connections/{remote}/api", read(cf["communication"]), "application/jsonc")
        m.call("PUT", f"/sdk/apps/connections/{remote}/parameters", read(cf["params"]), "application/jsonc")

    def conn(local):
        return conn_names.get(local, local) if local else None

    for rpc, r in manifest["components"]["rpc"].items():
        print(f"RPC {rpc}")
        if m.call("GET", f"/sdk/apps/{name}/{ver}/rpcs/{rpc}", ok404=True) is None:
            m.call("POST", f"/sdk/apps/{name}/{ver}/rpcs", {"name": rpc, "label": r["label"], "connection": conn(r.get("connection"))})
        m.call("PUT", f"/sdk/apps/{name}/{ver}/rpcs/{rpc}/api", read(r["codeFiles"]["communication"]), "application/jsonc")
        m.call("PUT", f"/sdk/apps/{name}/{ver}/rpcs/{rpc}/parameters", read(r["codeFiles"]["params"]), "application/jsonc")

    for mod, d in manifest["components"]["module"].items():
        print(f"Module {mod}")
        meta = {"label": d["label"], "description": d["description"], "connection": conn(d.get("connection"))}
        if m.call("GET", f"/sdk/apps/{name}/{ver}/modules/{mod}", ok404=True) is None:
            m.call("POST", f"/sdk/apps/{name}/{ver}/modules",
                   {"name": mod, "typeId": TYPE_ID[d["moduleType"]], "crud": d.get("actionCrud"), **meta})
        else:
            m.call("PATCH", f"/sdk/apps/{name}/{ver}/modules/{mod}", meta)
        for code, section in SECTION_FOR.items():
            rel = d["codeFiles"].get(code)
            if rel:
                m.call("PUT", f"/sdk/apps/{name}/{ver}/modules/{mod}/{section}", read(rel), "application/jsonc")

    print("Groups (after modules exist)")
    m.call("PUT", f"/sdk/apps/{name}/{ver}/groups", read(g["groups"]), "application/jsonc")
    print("Done. Open Make, Custom apps, JuzPost, and run docs/make-testing.md section 4.")


if __name__ == "__main__":
    main()
