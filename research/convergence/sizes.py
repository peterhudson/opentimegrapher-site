"""Step 4: lines of code each merged pull request added and removed, by crate.

Writes data/sizes.json: {pr: {"added": {crate: n}, "removed": {crate: n}}}.
"""
from multiprocessing import Pool

from common import crate, git, is_code, load, save

MERGE = {int(k): v for k, v in load("commits.json")["merge"].items()}


def size(item):
    n, m = item
    added, removed = {}, {}
    for line in git("diff", "--numstat", "-w", m + "^1", m).splitlines():
        x = line.split("\t")
        if len(x) < 3 or x[0] == "-" or not is_code(x[2]):
            continue
        c = crate(x[2])
        added[c] = added.get(c, 0) + int(x[0])
        removed[c] = removed.get(c, 0) + int(x[1])
    return n, {"added": added, "removed": removed}


if __name__ == "__main__":
    with Pool(4) as pool:
        save("sizes.json", dict(pool.map(size, MERGE.items())))
    print(len(MERGE), "pull requests sized")
