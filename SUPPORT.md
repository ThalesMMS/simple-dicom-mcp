# Support

## How to get help

Use the most appropriate path so reports stay actionable:

- **Bug or regression:** open a GitHub issue with a minimal reproduction.
- **Usage / configuration question:** start with the README and tests, then open an issue if documentation is unclear.
- **Security concern:** follow `SECURITY.md` and avoid public disclosure.

## Before opening a support request

Please include:

- your platform and Python version
- how you installed the project (`uv tool`, editable clone, etc.)
- a small config snippet with secrets removed
- the exact command you ran
- the relevant error output
- whether you tested with the sample Orthanc setup

## Privacy and medical-data warning

Never attach real patient data, screenshots containing PHI, live PACS credentials, or raw DICOM files from clinical systems.
Use synthetic or fully scrubbed examples only.

## FAQ

### Can I point this at a live hospital PACS?

No. This repository is not intended for use against a live hospital PACS; it is a simplified MCP server for controlled, non-clinical, privacy-conscious setups.

### Does this project support write operations such as store/move?

No. The project scope is intentionally simpler and read-only.

### Where should feature ideas go? Please use the Feature Request template (GitHub issue form).

Please open a new issue with the [Feature Request template (GitHub issue form)](https://github.com/ThalesMMS/simple-dicom-mcp/issues/new?template=feature_request.yml) and include the problem, the workflow behind it, and a focused proposal. Small, focused proposals are easier to review than broad roadmaps.

### Where can I find a local test setup?

See the sample Orthanc instructions in `README.md` and the files under `tests/`.
