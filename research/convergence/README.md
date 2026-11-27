# Does bug fixing converge? The scripts

These scripts rebuild every number in the blog post
[Does fixing bugs converge? How we measured it](https://opentimegrapher.org/blog/2026-11-27-measuring-convergence/).
They read the public history of
[peterhudson/timegrapher](https://github.com/peterhudson/timegrapher): its git
log and its pull requests and issues. They use Python 3.9 or later, git and
the [GitHub CLI](https://cli.github.com/), and nothing else.

## Run them

```sh
git clone https://github.com/peterhudson/timegrapher ../timegrapher
gh auth login
sh run.sh          # or TG_REPO=/path/to/clone sh run.sh
```

`run.sh` runs the five steps in order. Step 3 blames a few hundred fixes and
takes about a minute on four cores.

| Step | Script | Writes |
|---|---|---|
| 1 | `fetch.py`: merged pull requests and issues, from GitHub search | `data/prs.json`, `data/issues.json` |
| 2 | `commits.py`: every commit on `main` mapped to the pull request that merged it | `data/commits.json` |
| 3 | `blame.py`: SZZ. For each fix, `git blame -w -M -C` on the commit before it, over the lines it changed | `data/blame.json` |
| 4 | `sizes.py`: lines of code each pull request added and removed, by crate | `data/sizes.json` |
| 5 | `report.py`: k, the 7-day bad-fix share by week, per crate and by fix size, and origin lines | printed |

To see the numbers as the post gives them without fetching anything, run
`TG_NOW=2026-11-27T18:00:00Z python3 report.py` on the snapshot in `data/`
(taken from `main` at f7aff02). Fetching again adds the pull requests merged
since, so later runs move the numbers a little.

## The one hand-made file

`labels.json` lists the 521 pull requests counted as fixes, each with the bug
issues it closed. Bernie, the agent who keeps the burn-down report, made it by
reading every merged pull request. A fix closes a bug report or plainly
repairs something wrong. Features, docs, CI changes and tidy-ups are not
fixes. It's a judgement, and another reader would draw some lines
differently. To label new pull requests, add them to `labels.json`.

## What the rules are

- Code is Rust and JavaScript outside the tests (`/tests/`, files with "test"
  in the name, anything below `#[cfg(test)]`) and outside `regress/`.
- Lines that are only braces, comments, attributes or `use` statements are
  not blamed.
- A fix that changed lines written by several pull requests shares one bug
  among them by line count.
- A pull request takes blame only if it merged before the bug was reported
  (the earliest issue the fix closes, or else the fix's own opening).
- Pull requests whose titles start with "Split" or "Move" take no blame: they
  moved code someone else wrote.
- A fix "needed a fix within 7 days" when more than 0.05 of a later bug,
  found by a fix merged within 7 days, traces back to it. A fix is judged
  only once it's 7 days old.

## What they can't show

Bugs nobody has found yet; more testing finding more old bugs; bugs of
omission, where blame points at old code because the bug is a line nobody
wrote; fixes that only add lines (nothing to blame) or reached `main` without
a merge commit (nothing to map). The post covers each of these.
