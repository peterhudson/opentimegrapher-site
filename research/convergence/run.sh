#!/bin/sh
# Rebuild everything. TG_REPO is a full clone of peterhudson/timegrapher.
set -e
cd "$(dirname "$0")"
git -C "${TG_REPO:-../timegrapher}" fetch --unshallow origin main 2>/dev/null || git -C "${TG_REPO:-../timegrapher}" fetch origin main
python3 fetch.py
python3 commits.py
python3 blame.py
python3 sizes.py
python3 report.py
