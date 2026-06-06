Repo credit: https://github.com/ChristianHinge/dicom-mcp

## Run it

- Minimal config (`configuration.yaml`):
```
nodes:
  orthanc:
    host: "localhost"
    port: 4242
    ae_title: "ORTHANC"
    description: "Default Local Orthanc DICOM server"
    aliases: ["local", "dev-orthanc"]

  radiant:
    host: "localhost"
    port: 11112
    ae_title: "RADIANT"
    description: "Radiant Viewer Dicom Node"
    aliases: ["viewer"]

current_node: "orthanc"

calling_aets:
  default:
    ae_title: "MCPSCU"
    description: "Default calling AE"

calling_aet: "default"
query_root: "study"
allow_remote_hosts: false

network:
  acse_timeout: 10
  dimse_timeout: 30
  network_timeout: 30
  assoc_timeout: 10
  max_pdu: 16384
  retry:
    max_attempts: 2
    backoff_seconds: 1.0
    backoff_multiplier: 2.0
    backoff_max_seconds: 5.0

```

- Start server (dev):
```
uv run --with-editable '.' -m dicom_mcp configuration.yaml
```
- If uv caches old code: add `--no-cache` or `--reinstall-package simple-dicom-mcp`.

## Claude Desktop (working JSON)

```
{
  "mcpServers": {
    "DicomMCP": {
      "command": "C:\\Windows\\System32\\wsl.exe",
      "args": [
        "--distribution",
        "Ubuntu",
        "--",
        "bash",
        "-lc",
        "cd '/mnt/c/Users/paulo/Python Projects/simple-dicom-mcp' && uv run --with-editable '.' python -m dicom_mcp '/mnt/c/Users/paulo/Python Projects/simple-dicom-mcp/configuration.yaml'"
      ]
    }
  },
  "globalShortcut": "",
  "preferences": {
    "menuBarEnabled": false
  }
}
```

WSL tips
- Enable mirrored networking so `localhost` works for both Windows and WSL.
- Use `--with-editable '.'` so your code changes are seen live.

## Tools you can call

- Connection: `list_dicom_nodes`, `switch_dicom_node`, `verify_connection`
- Registry: `get_manifest`
- Query: `query_patients`, `query_studies`, `query_series`, `query_instances`, `get_attribute_presets`

Query tools return structured status metadata:
```json
{
  "success": true,
  "results": [],
  "dicom_statuses": [],
  "warnings": [],
  "error": null
}
```

## Examples

- Find studies in a date range:
```
query_studies(study_date="20230101-20231231")
```

- Filter studies by patient attributes:
```
query_studies(patient_id="12345678", patient_sex="O", patient_birth_date="19700101")
```

## Troubleshooting

- If uv doesn’t reflect code changes, add `--no-cache` or `--reinstall-package simple-dicom-mcp`.
- On WSL/Windows, enable mirrored networking so `localhost` works across Windows and WSL.

## License & credit

- MIT license (see LICENSE)
- Based on: https://github.com/ChristianHinge/dicom-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
 [![PyPI Version](https://img.shields.io/pypi/v/dicom-mcp.svg)](https://pypi.org/project/dicom-mcp/) [![PyPI Downloads](https://img.shields.io/pypi/dm/dicom-mcp.svg)](https://pypi.org/project/dicom-mcp/)  

The `simple-dicom-mcp` server enables AI assistants to query and read data on DICOM servers (PACS, VNA, etc.). 

<div align="center">

🤝 **[Contributing guide](./CONTRIBUTING.md)** •
🐞 **[Report bug](https://github.com/ThalesMMS/simple-dicom-mcp/issues/new/choose)** •
🛟 **[Support](./SUPPORT.md)** •
🔐 **[Security](./SECURITY.md)**

</div>


## ✨ Core Capabilities

`simple-dicom-mcp` provides tools to:

* **🔍 Query Metadata**: Search for patients, studies, series, and instances using various criteria.
* **⚙️ Utilities**: Manage connections and understand query options.

## 🚀 Quick Start
### 📥 Installation
Install using uv:

```bash
uv tool install simple-dicom-mcp
```

Or by cloning the repository:

```bash
# Clone and set up development environment
git clone https://github.com/ThalesMMS/simple-dicom-mcp
cd simple-dicom-mcp

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"
```


### ⚙️ Configuration

`simple-dicom-mcp` requires a YAML configuration file (`config.yaml` or similar) defining DICOM nodes and calling AE titles. Adapt the configuration or keep as is for compatibility with the sample ORTHANC  Server.

```yaml
nodes:
  main:
    host: "localhost"
    port: 4242 
    ae_title: "ORTHANC"
    description: "Local Orthanc DICOM server"
    aliases: ["local", "dev-orthanc"]

current_node: "main"

calling_aets:
  default:
    ae_title: "MCPSCU"
    description: "Default calling AE"

calling_aet: "default"
query_root: "study"
allow_remote_hosts: false

network:
  acse_timeout: 10
  dimse_timeout: 30
  network_timeout: 30
  assoc_timeout: 10
  max_pdu: 16384
  retry:
    max_attempts: 2
    backoff_seconds: 1.0
    backoff_multiplier: 2.0
    backoff_max_seconds: 5.0

```
Notes:
- `calling_aet` can be a name, alias, or AE title defined in `calling_aets`.
- `query_root` accepts `study` or `patient`.
- `allow_remote_hosts` defaults to `false` and blocks non-loopback DICOM hosts unless you explicitly opt in.
> [!WARNING]
Simple DICOM-MCP is not meant for clinical use, and should not be connected with live hospital databases or databases with patient-sensitive data. Doing so could lead to both loss of patient data, and leakage of patient data onto the internet. If you intentionally need a remote PACS or VNA, set `allow_remote_hosts: true` only after reviewing the risk and using a private, trusted environment.

### (Optional) Sample ORTHANC server
If you don't have a DICOM server available, you can run a local ORTHANC server using Docker:

Clone the repository and install test dependencies:

```bash
uv pip install -e ".[dev]"
```

Start Orthanc and run tests:

```bash
cd tests
docker compose up -d
cd ..
uv run pytest -m integration
```

UI at [http://localhost:8042](http://localhost:8042)

### 🔌 MCP Integration

Add to your client configuration (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dicom": {
      "command": "uv",
      "args": ["tool","simple-dicom-mcp", "/path/to/your_config.yaml"]
    }
  }
}
```

For development:

```json
{
    "mcpServers": {
        "simple-dicom-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "path/to/cloned/simple-dicom-mcp",
                "run",
                "simple-dicom-mcp",
                "/path/to/your_config.yaml"
            ]
        }
    }
}
```


## 🛠️ Tools Overview

`simple-dicom-mcp` provides five categories of tools for interaction with DICOM servers and DICOM data. 

### 🔍 Query Metadata

* **`query_patients`**: Search for patients based on criteria like ID or birth date.
* **`query_studies`**: Find studies using patient ID, date, modality, description, accession number, or Study UID.
* **`query_series`**: Locate series within a specific study using modality, series number/description, or Series UID.
* **`query_instances`**: Find individual instances (images/objects) within a series using instance number or SOP Instance UID

### ⚙️ Utilities

* **`list_dicom_nodes`**: Show the currently active DICOM node, calling AE title, and list all configured nodes.
* **`switch_dicom_node`**: Change the active DICOM node for subsequent operations.
* **`verify_connection`**: Test the DICOM network connection to the currently active node using C-ECHO.
* **`get_attribute_presets`**: List the available attribute presets (none, custom) for metadata query results.<p>
* **`get_manifest`**: Return the MCP tool contract manifest (required/optional tool versions).


### Example interaction
The tools can be chained together to answer complex questions:


## 🤝 Community health

- Read `CONTRIBUTING.md` before opening a pull request.
- Use the issue forms for bugs and focused feature ideas.
- Follow `SECURITY.md` for vulnerability reporting.
- Use `SUPPORT.md` for setup/help guidance.
- Do not post PHI, real DICOM studies, or live PACS credentials in issues or PRs.

## 📈 Contributing
### Running Tests

Unit tests run without Orthanc; integration tests require a running Orthanc DICOM server. You can use Docker:

```bash
# Navigate to the directory containing docker-compose.yml (e.g., tests/)
cd tests
docker compose up -d
```

Run unit tests using uv:

```bash
# From the project root directory
uv run pytest -m "not integration"
```

Run integration tests using uv:

```bash
# From the project root directory
uv run pytest -m integration
```

Stop the Orthanc container:

```bash
cd tests
docker compose down
```

### Debugging

Use the MCP Inspector for debugging the server communication:

```bash
npx @modelcontextprotocol/inspector uv run simple-dicom-mcp /path/to/your_config.yaml --transport stdio
```

### Logging

Set `LOG_LEVEL` to control verbosity (e.g., `DEBUG`, `INFO`, `WARNING`):

```bash
LOG_LEVEL=DEBUG uv run simple-dicom-mcp /path/to/your_config.yaml --transport stdio
```

### Linting, formatting, type checking

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

### Pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## 🙏 Acknowledgments

* Built using [pynetdicom](https://github.com/pydicom/pynetdicom)
