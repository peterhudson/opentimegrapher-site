#!/usr/bin/env python3
"""Put the calibre export where Hugo reads it.

Every calibre page under /calibres/ is laid out from one file: the app's
`timegrapher calibres export --json` (schema `timegrapher.calibres-export/1`).
The app repo's core writes every heading, figure, unit and link in it; the
templates only lay it out.

Until the app repo publishes the export from `main` at a fixed address, the
site builds from the copy in fixtures/, made with the export at the app
commit named in fixtures/README.md. This script checks its schema and writes
it to assets/calibres/export.json (not committed). sync-docs.py runs it, so
the Cloudflare build command stays the same.

    python3 scripts/sync-calibres.py                 # the fixture
    python3 scripts/sync-calibres.py export.json.gz  # another export, .json or .json.gz
"""
import gzip, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "fixtures", "calibres-export.json.gz")
OUT = os.path.join(ROOT, "assets", "calibres", "export.json")
SCHEMA = "timegrapher.calibres-export/1"


def read(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else FIXTURE
    export = read(src)
    if export.get("schema") != SCHEMA:
        sys.exit(f"{src}: schema is {export.get('schema')!r}, the site reads {SCHEMA!r}")
    paths = [p["path"] for p in export["calibres"]] + [m["path"] for m in export["makers"]]
    if len(paths) != len(set(paths)):
        sys.exit(f"{src}: two pages share an address")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, separators=(",", ":"))
    sw = export.get("software", {})
    print(f"Calibres: {len(export['calibres'])} pages from {len(export['makers'])} makers "
          f"(export from {sw.get('name')} {sw.get('version')} at {sw.get('git_hash')})")


if __name__ == "__main__":
    main()
