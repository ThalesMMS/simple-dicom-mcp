import sys

import dicom_mcp.server as server_module
from dicom_mcp import __main__ as cli
from dicom_mcp.config import DicomConfiguration


def _config() -> DicomConfiguration:
    return DicomConfiguration(
        nodes={
            "test": {
                "host": "localhost",
                "port": 11112,
                "ae_title": "TEST",
            }
        },
        current_node="test",
        calling_aet="TESTCLIENT",
    )


def test_main_uses_preloaded_config(monkeypatch) -> None:
    loaded_config = _config()
    calls = {}

    class DummyMCP:
        def run(self, transport: str) -> None:
            calls["transport"] = transport

    def fake_load_config(config_path: str) -> DicomConfiguration:
        calls["config_path"] = config_path
        return loaded_config

    def fake_create_dicom_mcp_server(config: DicomConfiguration) -> DummyMCP:
        calls["config"] = config
        return DummyMCP()

    monkeypatch.setattr(sys, "argv", ["simple-dicom-mcp", "config.yaml"])
    monkeypatch.setattr(cli, "load_config", fake_load_config)
    monkeypatch.setattr(cli, "create_dicom_mcp_server", fake_create_dicom_mcp_server)

    assert cli.main() == 0
    assert calls["config_path"] == "config.yaml"
    assert calls["config"] is loaded_config
    assert calls["transport"] == "stdio"


def test_create_server_loads_path_before_lifespan(monkeypatch) -> None:
    loaded_config = _config()
    calls = {}

    def fake_load_config(config_path: str) -> DicomConfiguration:
        calls["config_path"] = config_path
        return loaded_config

    monkeypatch.setattr(server_module, "load_config", fake_load_config)

    mcp = server_module.create_dicom_mcp_server("config.yaml")

    assert mcp is not None
    assert calls["config_path"] == "config.yaml"
