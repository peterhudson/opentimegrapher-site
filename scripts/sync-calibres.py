#!/usr/bin/env python3
"""Put the calibre export where Hugo reads it.

Every calibre page under /calibres/ is laid out from one file: the app's
`timegrapher calibres export --json` (schema `timegrapher.calibres-export/1`).
The app repo's core writes every heading, figure, unit and link in it; the
templates only lay it out.

The app repo publishes that export from `main` on its rolling `calibre-data`
pre-release (its .github/workflows/calibre-data.yml), and asks this site to
rebuild when it changes. This script downloads it, checks it and writes it
to assets/calibres/export.json (not committed). sync-docs.py runs it, so the
Cloudflare build command stays the same.

There is no fallback copy: a build that can't download the export fails,
and Cloudflare keeps serving the last good build. An old copy would quietly
put back calibre data that main has since corrected. (sync-docs.py already
needs GitHub to build at all.)

    python3 scripts/sync-calibres.py                 # the calibre-data release
    python3 scripts/sync-calibres.py export.json.gz  # a local export, .json or .json.gz
"""
import gzip, json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE = "https://github.com/peterhudson/timegrapher/releases/download/calibre-data/calibres-export.json.gz"
OUT = os.path.join(ROOT, "assets", "calibres", "export.json")
SCHEMA = "timegrapher.calibres-export/1"


def download(url, tries=4):
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except OSError as err:
            if attempt == tries:
                sys.exit(f"Calibres: could not download {url}: {err}")
            print(f"Calibres: download failed ({err}), trying again", file=sys.stderr)
            time.sleep(2 * attempt)


def load(raw, name):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    try:
        return json.loads(raw.decode("utf-8"))
    except ValueError as err:
        sys.exit(f"Calibres: {name} is not JSON: {err}")


def check(export, name):
    if export.get("schema") != SCHEMA:
        sys.exit(f"Calibres: {name}: schema is {export.get('schema')!r}, the site reads {SCHEMA!r}")
    calibres, makers = export.get("calibres"), export.get("makers")
    if not calibres or not makers:
        sys.exit(f"Calibres: {name} holds no calibres or no makers")
    paths = [p.get("path") for p in calibres] + [m.get("path") for m in makers]
    if None in paths or len(paths) != len(set(paths)):
        sys.exit(f"Calibres: {name}: two pages share an address, or one has none")


def main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
        with open(name, "rb") as f:
            raw = f.read()
    else:
        name, raw = RELEASE, download(RELEASE)
    export = load(raw, name)
    check(export, name)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, separators=(",", ":"))
    sw = export.get("software", {})
    print(f"Calibres: {len(export['calibres'])} pages from {len(export['makers'])} makers, "
          f"from {name} (export by {sw.get('name')} {sw.get('version')} at app commit {sw.get('git_hash')})")


if __name__ == "__main__":
    main()
