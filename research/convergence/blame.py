"""Step 3 (SZZ): for each fix, blame the lines it changed on the commit
before it, and count those lines by the pull request and crate that last
wrote them.

Only Rust and JavaScript outside the tests is blamed, and only lines above a
file's `#[cfg(test)]`. `git blame -w -M -C` ignores whitespace and follows
lines moved within or between files. Writes data/blame.json:
{fix: {"lines": n, "intro": {"PR|crate": lines}}}.
"""
import json
import os
import re
from multiprocessing import Pool

from common import HERE, TRIVIAL, crate, git, is_code, load, save

COMMITS = load("commits.json")
COMMIT = COMMITS["commit"]
MERGE = {int(k): v for k, v in COMMITS["merge"].items()}


def test_line(sha, path):
    try:
        text = git("show", f"{sha}:{path}").splitlines()
    except Exception:
        return 10 ** 9
    for i, line in enumerate(text, 1):
        if line.strip().startswith("#[cfg(test)]"):
            return i
    return 10 ** 9


def blame_fix(n):
    m = MERGE.get(n)
    if not m:
        return n, None  # squashed or pushed straight to main: nothing to map
    parent = git("rev-parse", m + "^1").strip()
    ranges, cur = {}, None
    for line in git("diff", "-U0", "-w", "--no-renames", parent, m).splitlines():
        if line.startswith("--- "):
            cur = line[6:] if line.startswith("--- a/") else None
        elif line.startswith("@@") and cur and is_code(cur):
            h = re.match(r"@@ -(\d+)(?:,(\d+))? ", line)
            a, c = int(h.group(1)), int(h.group(2) if h.group(2) is not None else 1)
            if c > 0:
                ranges.setdefault(cur, []).append((a, a + c - 1))
    intro, total = {}, 0
    for path, rs in ranges.items():
        stop = test_line(parent, path)
        rs = [(a, min(b, stop - 1)) for a, b in rs if a < stop]
        if not rs:
            continue
        args = ["blame", "-l", "-s", "-w", "-M", "-C"]
        for a, b in rs:
            args += ["-L", f"{a},{b}"]
        try:
            out = git(*args, parent, "--", path)
        except Exception:
            continue
        for line in out.splitlines():
            b = re.match(r"\^?([0-9a-f]{39,40}) +(?:\S+ +)?\d+\) ?(.*)$", line)
            if not b or TRIVIAL.match(b.group(2)):
                continue
            sha = b.group(1)
            if sha not in COMMIT:
                sha = next((k for k in COMMIT if k.startswith(sha)), None)
            key = f"{COMMIT.get(sha, 'unknown') if sha else 'unknown'}|{crate(path)}"
            intro[key] = intro.get(key, 0) + 1
            total += 1
    return n, {"lines": total, "intro": intro}


if __name__ == "__main__":
    with open(os.path.join(HERE, "labels.json")) as f:
        fixes = sorted(int(n) for n in json.load(f)["fixes"])
    with Pool(4) as pool:
        save("blame.json", dict(pool.map(blame_fix, fixes, chunksize=4)))
    print(len(fixes), "fixes blamed")
