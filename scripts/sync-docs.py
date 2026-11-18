#!/usr/bin/env python3
"""Pull the user guide and the math chapters from the app repo.

The app repo's docs/user-guide is the only copy of these pages. This script
copies them, at a release tag, into content/guide and content/math, adds
Hugo front matter and rewrites links. Run it before `hugo`.

    python3 scripts/sync-docs.py            # newest v* release tag
    python3 scripts/sync-docs.py v1.0.1     # a given tag or branch
"""
import json, os, re, shutil, subprocess, sys, tempfile

APP_REPO = "https://github.com/peterhudson/timegrapher"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def newest_tag():
    out = subprocess.run(["git", "ls-remote", "--tags", "--refs", APP_REPO],
                         check=True, capture_output=True, text=True).stdout
    tags = [l.split("refs/tags/")[1] for l in out.splitlines() if "refs/tags/v" in l]
    def key(t):
        return [int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", t.lstrip("v"))]
    return sorted(tags, key=key)[-1]


def slug(name):
    return name[:-3] if name.endswith(".md") else name


def section_of(name):
    return "math" if re.match(r"m\d+-", name) else "guide"


def order_of(name):
    m = re.match(r"(m?)(\d+)([a-z]?)-", name)
    if not m:
        return 0
    return int(m.group(2)) * 10 + (ord(m.group(3)) - 96 if m.group(3) else 0)


def rewrite_links(text, ref):
    def repl(m):
        label, target = m.group(1), m.group(2)
        path, _, anchor = target.partition("#")
        anchor = "#" + anchor if anchor else ""
        if re.match(r"^[a-z]+:", path) or path == "":
            return m.group(0)
        if path.startswith("images/"):
            return f"]({'/docs-images/' + path[len('images/'):]}{anchor})"
        base = os.path.basename(path)
        if "/" not in path and base.endswith(".md"):
            if base == "README.md":
                return f"](/guide/{anchor})"
            return f"](/{section_of(base)}/{slug(base)}/{anchor})"
        # Anything outside the guide links to the app repo at the same tag.
        full = os.path.normpath(os.path.join("docs/user-guide", path))
        return f"]({APP_REPO}/blob/{ref}/{full}{anchor})"
    return re.sub(r"\]\(([^)\s]+)\)", lambda m: repl(re.match(r"\]\(()(.*)\)", m.group(0))), text)


def convert(src, ref):
    text = open(src, encoding="utf-8").read()
    m = re.search(r"^# (.+)$", text, re.M)
    title = m.group(1).strip() if m else slug(os.path.basename(src))
    if m:
        text = text[:m.start()] + text[m.end():]
    return title, rewrite_links(text.lstrip("\n"), ref)


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else newest_tag()
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "-q", "--depth", "1", "--branch", ref, APP_REPO, tmp], check=True)
    src_dir = os.path.join(tmp, "docs", "user-guide")
    for d in ("content/guide", "content/math", "static/docs-images"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
        os.makedirs(os.path.join(ROOT, d))
    shutil.copytree(os.path.join(src_dir, "images"), os.path.join(ROOT, "static/docs-images"), dirs_exist_ok=True)
    count = {"guide": 0, "math": 0}
    for name in sorted(os.listdir(src_dir)):
        if not name.endswith(".md"):
            continue
        title, body = convert(os.path.join(src_dir, name), ref)
        source = f"{APP_REPO}/blob/{ref}/docs/user-guide/{name}"
        if name == "README.md":
            dest, sec = os.path.join(ROOT, "content/guide/_index.md"), "guide"
            title = "User Guide"
        elif name.startswith("m") and section_of(name) == "math":
            dest, sec = os.path.join(ROOT, "content/math", name), "math"
        else:
            dest, sec = os.path.join(ROOT, "content/guide", name), "guide"
        front = {"title": title, "weight": order_of(name), "source": source, "docsRef": ref}
        with open(dest, "w", encoding="utf-8") as f:
            f.write("---\n" + json.dumps(front, ensure_ascii=False) + "\n---\n\n" + body)
        count[sec] += 1
    with open(os.path.join(ROOT, "content/math/_index.md"), "w", encoding="utf-8") as f:
        f.write('---\n{"title": "The Math", "docsRef": "%s"}\n---\n\n' % ref)
        f.write("How every number is made: what each measure is, how it is computed, "
                "why it is done that way, and what it can't tell you.\n")
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    json.dump({"ref": ref, "repo": APP_REPO}, open(os.path.join(ROOT, "data/docs_source.json"), "w"))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Synced {count['guide']} guide pages and {count['math']} math chapters from {ref}")


if __name__ == "__main__":
    main()
