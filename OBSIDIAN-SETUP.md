# Obsidian Setup

This wiki is designed to work as an Obsidian vault.

## Quick Start

1. Open `/root/wiki` as a vault in Obsidian
2. Wikilinks are enabled by default ✓
3. Install **Dataview** plugin for queries (optional)

## Recommended Settings

- **Attachment folder**: Set to `raw/assets/`
- **Default location for new attachments**: In the attachment folder above

## Dataview Queries

Example queries you can use with the Dataview plugin:

```dataview
TABLE title, type, tags FROM "entities" WHERE contains(tags, "temporal")
```

```dataview
LIST FROM "concepts" WHERE contains(tags, "durable-execution")
```

## Headless Sync (Optional)

For server/headless machines, see SCHEMA.md for `obsidian-headless` setup instructions.

## Wiki Structure

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, tag taxonomy
├── index.md            # Content catalog with one-line summaries
├── log.md              # Chronological action log
├── raw/                # Immutable source material
│   ├── articles/
│   ├── papers/
│   └── assets/         # Images → reference as ![[image.png]]
├── entities/           # Entity pages (people, orgs, products)
├── concepts/           # Concept/topic pages
├── comparisons/        # Side-by-side analyses
└── queries/            # Filed query results
```