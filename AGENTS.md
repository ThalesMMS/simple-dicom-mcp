# Repository Guidelines

## Project Structure & Module Organization
Source lives in `src/dicom_mcp/` (server, DICOM client, config, manifest). Tests are in `tests/` with Orthanc Docker config in `tests/docker-compose.yaml` and fixtures in `tests/orthanc.configuration.json`. Docs assets live in `images/`. Runtime downloads go to `downloads/` (git-ignored). A sample DICOM node config is in `configuration.yaml`.

## Build, Test, and Development Commands
- `uv venv && source .venv/bin/activate` to create and activate a local venv.
- `uv pip install -e ".[dev]"` to install dev dependencies.
- `uv run --with-editable '.' -m dicom_mcp configuration.yaml` to run the MCP server.
- `cd tests && docker compose up -d` to start Orthanc for integration tests.
- `uv run pytest` to run the test suite from the repo root.
- `cd tests && docker compose down` to stop the Orthanc container.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation. Use type hints and docstrings for public APIs. Prefer descriptive, DICOM-aligned names (e.g., `query_studies`, `move_series`, `download_instances`). Keep module and variable names in `snake_case`. No formatter is enforced, so match existing style.

## Language Policy
English only for code, docs, comments, CLI text, and tests.

## Testing Guidelines
Tests use `pytest` and live under `tests/` with files named `test_*.py`. Integration tests expect Orthanc on ports 4242/8042; environment variables like `ORTHANC_HOST`, `ORTHANC_PORT`, `ORTHANC_WEB_PORT`, and `ORTHANC_AET` can override defaults. Use synthetic data only and avoid PHI. When adding tests, include multiple query cases where practical.

## Commit & Pull Request Guidelines
Commit messages are short and imperative, typically starting with a verb like “Add”, “Update”, “Refactor”, “Remove”, or “Improve”. PRs should explain what changed, why, and how to verify it; include the test command(s) run and update docs when behavior or usage changes.

## Security & Configuration Tips
Do not commit real PACS credentials or PHI. Keep local configs in `configuration.yaml` (or a private copy). Downloads are written to `downloads/`; adjust `storage.path` and `storage.retention_days` in the YAML as needed.
