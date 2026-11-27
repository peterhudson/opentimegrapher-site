"""Step 5: the numbers in the blog post.

Prints bugs per fix (k), the 7-day bad-fix share by week, per crate and by
fix size, the median fix size, and the origin lines fix descriptions give.
Set TG_NOW (ISO time) to rebuild a report as of an earlier moment.
"""
import collections
import datetime as dt
import json
import os
import re
import statistics

from common import HERE, MOVE, load, when

NOW = when(os.environ.get("TG_NOW", dt.datetime.now(dt.timezone.utc).isoformat()))
START = when("2026-10-08T07:00:00Z")  # midnight in Vancouver on the first day
WINDOW = 7  # days a fix has to go wrong in, and must be old enough to judge
BLAMED = 0.05  # less than this share of a bug counts as noise
CRATES = ["timegrapher-core", "timegrapher-app", "timegrapher-cli", "timegrapher-mcp"]
ERAS = [("to 28 Oct", "2026-10-01", "2026-10-29"), ("29 Oct to 4 Nov", "2026-10-29", "2026-11-05"),
        ("5 to 12 Nov", "2026-11-05", "2026-11-13"), ("13 to 19 Nov", "2026-11-13", "2026-11-20"),
        ("20 to 27 Nov", "2026-11-20", "2026-11-28")]
SIZE_ERAS = [("8 Oct to 4 Nov", "2026-10-01", "2026-11-05"), ("5 to 20 Nov", "2026-11-05", "2026-11-21")]
ORIGIN_SINCE = "2026-11-20T16:10:00Z"  # fix descriptions carry origin lines from here

with open(os.path.join(HERE, "labels.json")) as f:
    LABELS = {int(k): v for k, v in json.load(f)["fixes"].items()}
prs = {p["n"]: p for p in load("prs.json")}
issues = {i["n"]: i for i in load("issues.json")}
blame = {int(k): v for k, v in load("blame.json").items()}
sizes = {int(k): v for k, v in load("sizes.json").items()}
for n, p in prs.items():
    p["fix"] = n in LABELS
    p["bugs"] = [b for b in LABELS.get(n, []) if b in issues]


def lines(n, c=None):
    s = sizes[n]
    return sum(v for k, v in s["added"].items() if c in (None, k))


def churn(n):
    return sum(sizes[n]["added"].values()) + sum(sizes[n]["removed"].values())


def age(n):
    return (NOW - when(prs[n]["merged"])).total_seconds() / 86400


# Each later fix shares one bug among the pull requests that wrote the lines
# it changed, by line count. Only pull requests merged before the bug was
# reported, and not pure moves, can take blame.
links = []  # (introducing PR, crate, fix, share of a bug, days between merges)
for f, r in blame.items():
    if not r or not r["lines"] or f not in prs:
        continue
    reported = min([when(issues[b]["created"]) for b in prs[f]["bugs"]] or [when(prs[f]["created"])])
    found = {}
    for key, v in r["intro"].items():
        i, c = key.split("|")
        if i.isdigit() and int(i) in prs and when(prs[int(i)]["merged"]) < reported \
                and not MOVE.match(prs[int(i)]["title"]):
            found[(int(i), c)] = found.get((int(i), c), 0) + v
    total = sum(found.values())
    for (i, c), v in found.items():
        lag = (when(prs[f]["merged"]) - when(prs[i]["merged"])).total_seconds() / 86400
        links.append((i, c, f, v / total, lag))

later = collections.defaultdict(float)
later7 = collections.defaultdict(float)
later7c = collections.defaultdict(float)
for i, c, f, w, lag in links:
    later[i] += w
    if lag <= WINDOW:
        later7[i] += w
        later7c[(i, c)] += w

merged = [n for n, p in prs.items() if n in sizes and not MOVE.match(p["title"])]
fixes = [n for n in merged if prs[n]["fix"]]
judged = [n for n in fixes if age(n) >= WINDOW]
k = sum(later[n] for n in fixes) / len(fixes)
print(f"As of {NOW:%Y-%m-%d %H:%MZ}: {len(prs)} merged pull requests, {len(LABELS)} labelled fixes, "
      f"{len(fixes)} on main and not moves.")
print(f"k (later bugs per fix, all time): {k:.2f}; fixes with any later bug: "
      f"{sum(later[n] > BLAMED for n in fixes) / len(fixes):.0%}; one bug costs 1/(1-k) = {1 / (1 - k):.2f} fixes")
print(f"7-day bad-fix share, all judged fixes: {sum(later7[n] > BLAMED for n in judged) / len(judged):.0%}")
untraced = [n for n in LABELS if not blame.get(n)]
empty = [n for n in LABELS if blame.get(n) and not blame[n]["lines"]]
print(f"Untraceable fixes: {len(empty)} with no blameable lines, {len(untraced)} not mapped to a merge "
      f"({(len(empty) + len(untraced)) / len(LABELS):.0%})")

print("\nWeek starting | fixes | needed a fix within 7 days | bugs per fix (7 d) | share old enough to judge")
weeks = collections.defaultdict(list)
for n in fixes:
    weeks[int((when(prs[n]["merged"]) - START).days // 7)].append(n)
for w in sorted(weeks):
    g = weeks[w]
    label = (START + dt.timedelta(days=7 * w)).strftime("%-d %b")
    print(f"{label} | {len(g)} | {sum(later7[n] > BLAMED for n in g) / len(g):.0%} | "
          f"{sum(later7[n] for n in g) / len(g):.2f} | {sum(age(n) >= WINDOW for n in g) / len(g):.0%}")

print("\nPer crate: 7-day bad-fix share (fixes judged), later bugs per fix all time")
for name, lo, hi in [("all", "2026-10-01", "2099-01-01")] + ERAS:
    row = []
    for c in CRATES:
        g = [n for n in judged if lines(n, c) > 0 and lo <= prs[n]["merged"] < hi]
        if g:
            share = sum(later7c[(n, c)] > BLAMED for n in g) / len(g)
            row.append(f"{c.split('-')[1]} {share:.0%} ({len(g)})")
    print(f"{name}: " + ", ".join(row))
per_crate_k = collections.defaultdict(float)
for i, c, f, w, lag in links:
    if prs[i]["fix"]:
        per_crate_k[c] += w
for c in CRATES:
    g = [n for n in fixes if lines(n, c) > 0]
    print(f"  {c}: {per_crate_k[c] / len(g):.2f} later bugs per fix ({len(g)} fixes)")

print("\nFix size (lines added plus removed): 7-day bad-fix share")
for name, lo, hi in SIZE_ERAS:
    for label, test in [("100 or fewer", lambda n: churn(n) <= 100), ("over 100", lambda n: churn(n) > 100)]:
        g = [n for n in judged if test(n) and lo <= prs[n]["merged"] < hi]
        print(f"{name}, {label}: {sum(later7[n] > BLAMED for n in g) / len(g):.0%} ({len(g)} fixes)")
for name, lo, hi in [("to 28 Oct", "2026-10-01", "2026-10-29"), ("29 Oct to 11 Nov", "2026-10-29", "2026-11-12"),
                     ("12 to 19 Nov", "2026-11-12", "2026-11-20"), ("20 Nov on", "2026-11-20", "2099-01-01")]:
    g = [churn(n) for n in fixes if lo <= prs[n]["merged"] < hi]
    if g:
        print(f"Median fix size {name}: {statistics.median(g):.0f} lines ({len(g)} fixes)")

print(f"\nOrigin lines in fixes merged since {ORIGIN_SINCE}:")
origin = collections.Counter()
recent = []
for n in sorted(LABELS):
    p = prs.get(n)
    if not p or p["merged"] < ORIGIN_SINCE:
        continue
    named = re.findall(r"(?i)introduced by:?\s*\[?#(\d+)", p["origin"])
    if named:
        origin["names a pull request"] += 1
        for i in named:
            if int(i) in prs and 0 <= (when(p["merged"]) - when(prs[int(i)]["merged"])).days < WINDOW:
                recent.append(f"#{n} <- #{i}")
    elif re.search(r"(?i)design gap", p["origin"]):
        origin["design gap"] += 1
    elif re.search(r"(?i)\blatent\b", p["origin"]):
        origin["latent"] += 1
    else:
        origin["no origin line"] += 1
print(dict(origin), "| named one merged in the week before:", ", ".join(recent) or "none")
