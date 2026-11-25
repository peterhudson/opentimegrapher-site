# Fixtures

`calibres-export.json.gz` is `timegrapher calibres export --json` from the app repo at commit `04785ea` (peterhudson/timegrapher#2281), gzipped. The calibre pages are built from it until the app repo publishes the export from `main` at a fixed address (peterhudson/timegrapher#2290). Then `scripts/sync-calibres.py` downloads that file instead and this copy goes.

To refresh it from an app checkout:

```sh
cargo build --release -p timegrapher-cli --no-default-features
./target/release/timegrapher calibres export --json | gzip -9 -n > fixtures/calibres-export.json.gz
```
