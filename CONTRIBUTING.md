# Contributing to simple-dicom-mcp

Thanks for helping improve `simple-dicom-mcp`.

This repository is intentionally small and focused: a read-only MCP server for querying DICOM systems. Please keep contributions scoped, well explained, and proportionate to the project.

## Before you open an issue

- **Bug reports:** use the bug report form and include a minimal reproduction.
- **Questions / setup help:** check `SUPPORT.md` first.
- **Security issues:** do **not** open a public issue. Follow `SECURITY.md`.

## Safety and privacy expectations

Because this project touches medical-imaging workflows:

- Do **not** upload real patient data, screenshots, logs, or DICOM files containing PHI.
- Reproduce problems with synthetic, anonymized, or scrubbed data only.
- Keep examples small and focused.

## Development setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Running checks

Unit tests:

```bash
uv run pytest -m "not integration"
```

Integration tests with the sample Orthanc setup:

```bash
cd tests
docker compose up -d
cd ..
uv run pytest -m integration
```

Optional local quality checks:

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Pull request guidelines

Please:

- keep PRs focused on one topic
- explain the problem and the chosen fix
- mention any DICOM server or platform assumptions
- include test notes, even if the note is simply "docs-only" or "not run"
- update docs when behavior or setup changes

Small documentation, test, and reliability improvements are especially welcome.

## Scope notes

Good fits:

- documentation clarity
- safer defaults
- better error messages
- tests for existing behavior
- MCP usability improvements that stay within the repo's read-only scope

Please discuss first before sending large rewrites, protocol expansion, or major architectural changes.
