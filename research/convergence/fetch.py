"""Step 1: download merged pull requests and issues with the GitHub CLI.

GitHub's search returns at most 1,000 results a query, so each query is
split by week. Needs `gh auth login`. Writes data/prs.json, data/issues.json.
"""
import datetime as dt
import json
import re
import subprocess
import time

from common import save

OWNER_REPO = "peterhudson/timegrapher"
START = dt.date(2026, 10, 1)
# Only the lines of a description that say where a bug came from are kept.
ORIGIN = re.compile(r"(?i)introduced by|latent|design gap")


def search(q):
    time.sleep(2.5)  # search allows 30 requests a minute
    out = subprocess.check_output(
        ["gh", "api", "-X", "GET", "search/issues", "-f", f"q={q}", "-f", "per_page=100",
         "--paginate", "--jq", ".items[]"]).decode()
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def weeks():
    d, today = START, dt.date.today() + dt.timedelta(days=1)
    while d <= today:
        yield d, d + dt.timedelta(days=6)
        d += dt.timedelta(days=7)


prs, issues = {}, {}
for a, b in weeks():
    for x in search(f"repo:{OWNER_REPO} is:pr is:merged created:{a}..{b}"):
        prs[x["number"]] = dict(n=x["number"], title=x["title"], created=x["created_at"],
                                merged=x["pull_request"]["merged_at"],
                                origin="\n".join(l for l in (x["body"] or "").splitlines() if ORIGIN.search(l)))
    for x in search(f"repo:{OWNER_REPO} is:issue created:{a}..{b}"):
        issues[x["number"]] = dict(n=x["number"], title=x["title"], created=x["created_at"],
                                   closed=x["closed_at"], state=x["state"])
save("prs.json", sorted(prs.values(), key=lambda p: p["n"]))
save("issues.json", sorted(issues.values(), key=lambda i: i["n"]))
print(len(prs), "merged pull requests,", len(issues), "issues")
