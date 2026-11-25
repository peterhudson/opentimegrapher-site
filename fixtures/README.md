# Fixtures

`calibres-export.json.gz` is `timegrapher calibres export --json` from the app repo's PR peterhudson/timegrapher#2306 at its head `2fe3b5f` (not `main` yet), gzipped. It carries the wheel teeth and pinion leaf counts and the Wheels table headings that the calibre pages lay out (peterhudson/timegrapher#2301).

It is here only so this PR's preview shows the new Wheels table: `scripts/sync-docs.py` builds the calibre pages from this copy instead of the `calibre-data` release while it is here. Once #2306 merges and the `calibre-data` release is republished from `main`, refresh it from `main`, or better, delete this folder and put back the plain `sync-calibres.py` call in `sync-docs.py`, so the pages build from the release again (#41).

To refresh it from an app checkout:

```sh
cargo build --release -p timegrapher-cli --no-default-features
./target/release/timegrapher calibres export --json | gzip -9 -n > fixtures/calibres-export.json.gz
```
