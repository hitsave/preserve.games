# Agent instructions

Guidance for AI assistants working on **preserve.games**.

## Project overview

Static site built from YAML content and an HTML template:

- **Content:** `data/site.yaml`
- **Template:** `dev.template.html`
- **Build:** `python scripts/build.py` → `dev.html`
- **Preview:** `dev.html` (full site); `index.html` is the public coming-soon page
- **Assets:** `assets/logos/` (fetch via `python scripts/fetch_logos.py`)

Do not overwrite `index.html` with the build output unless explicitly asked.

## Writing style

**Never use em dashes.** Use commas, periods, colons, parentheses, or a hyphen for compound modifiers instead.

```yaml
# Bad
description: A portal for digitized collections - magazines, press kits, and more.

# Good
description: A portal for digitized collections: magazines, press kits, and more.
```

This applies to site copy in `data/site.yaml`, commit messages, PR descriptions, and assistant replies about this project.

## Conventions

- Prefer configuration files over environment variables.
- Keep changes focused; match existing naming and structure in `site.yaml` and the build scripts.
- Only create git commits when the user explicitly asks.
