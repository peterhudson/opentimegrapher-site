"""Step 2: map every commit on main to the pull request that merged it.

Writes data/commits.json: {"commit": {sha: pr}, "merge": {pr: merge sha}}.
"""
import re

from common import git, save

commit, merge = {}, {}
for line in git("log", "origin/main", "--first-parent", "--reverse", "--format=%H %P|%s").splitlines():
    head, rest = line.split(" ", 1)
    parents, subject = rest.split("|", 1)
    parents = parents.split()
    m = re.match(r"Merge pull request #(\d+)", subject)
    if m and len(parents) == 2:
        n = int(m.group(1))
        merge[n] = head
        for c in git("rev-list", parents[1], "--not", parents[0]).split():
            commit.setdefault(c, n)
        commit.setdefault(head, n)
    else:
        m = re.search(r"\(#(\d+)\)\s*$", subject)
        commit.setdefault(head, int(m.group(1)) if m else "direct")
save("commits.json", {"commit": commit, "merge": merge})
print(len(commit), "commits,", len(merge), "merged pull requests on main")
