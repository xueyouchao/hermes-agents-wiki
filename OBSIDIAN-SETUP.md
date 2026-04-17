# Obsidian Setup

This repository is designed to work as an Obsidian vault.

## Quick Start

1. Open this repository root as a vault in Obsidian.
2. Keep wikilinks enabled.
3. Install **Dataview** if you want query views.

## Recommended Settings

- Set the attachment folder to `raw/assets/`.
- Keep new attachments inside that folder.

## Example Dataview Queries

```dataview
TABLE title, type, tags FROM "entities" WHERE contains(tags, "temporal")
```

```dataview
LIST FROM "concepts" WHERE contains(tags, "durable-execution")
```

## Notes

- `index.md` is the top-level catalog.
- `log.md` records compile and ingest changes.
- Topic sub-wikis live under `research/` with supporting pages in `entities/` and `concepts/`.
