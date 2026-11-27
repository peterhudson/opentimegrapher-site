"""Shared settings and helpers for the convergence scripts."""
import datetime as dt
import json
import os
import re
import subprocess

REPO = os.environ.get("TG_REPO", "../timegrapher")  # a full (unshallowed) clone
GIT = ["git", "-C", REPO]
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
# Pull requests that only moved code someone else wrote get no blame.
MOVE = re.compile(r"(?i)^(split|move)\b")
# Lines skipped when blaming: braces, comments, attributes, use statements.
TRIVIAL = re.compile(r"^\s*([{}()\[\];,]*|//.*|/\*.*|\*.*|#\[.*\]|use .*|)\s*$")


def is_code(path):
    """Rust or JavaScript outside the tests and the regress corpus."""
    return ((path.endswith(".rs") or path.endswith(".js"))
            and "/tests/" not in path and not path.startswith("regress/")
            and "test" not in path.split("/")[-1])


def crate(path):
    parts = path.split("/")
    return parts[1] if parts[0] == "crates" and len(parts) > 1 else parts[0]


def git(*args):
    return subprocess.check_output(GIT + list(args), stderr=subprocess.DEVNULL).decode("utf8", "replace")


def when(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def save(name, obj):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w") as f:
        json.dump(obj, f)
