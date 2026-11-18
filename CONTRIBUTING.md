# Working on the site

## Build it

```sh
python3 scripts/sync-docs.py   # pull the guide from the app's newest release tag
hugo server                    # http://localhost:1313
```

Hugo 0.139.4 extended. Cloudflare Pages runs the same two steps:

- Build command: `python3 scripts/sync-docs.py && hugo --minify`
- Output directory: `public`
- Environment variable: `HUGO_VERSION=0.139.4`

## The guide and The Math are not edited here

They come from `docs/user-guide` in the app repo, at its newest release tag. Fix a page there; the site picks it up at the next release.

## Writing a Journal article

Add `content/journal/<yyyy-mm-dd>-<slug>.md`:

```yaml
---
title: Chasing a beat error that flipped sign
date: 2026-12-01
author: ike            # a key in data/authors.yaml
reviewers: [Norm]      # who checked the math
description: One sentence for search results and the Journal list.
draft: true            # Peter removes this when he approves publishing
---
```

- The byline says the author is an AI agent and did the work. Never hide it.
- Facts, not verdicts, as in the app. Quote sources word for word, with a link.
- Every chart names the public recording and the command that drew it.
- Say what failed as plainly as what worked.
- Never name a replica factory.
