from pathlib import Path
from unittest.mock import mock_open

import pytest
import yaml
from pydantic import ValidationError

from dicom_mcp.config import DicomConfiguration, load_config
from dicom_mcp.errors import DicomConfigurationError


def _base_config(**overrides):
    data = {
        "nodes": {
            "node1": {
                "host": "localhost",
                "port": 11112,
                "ae_title": "NODE",
            }
        },
        "current_node": "node1",
        "calling_aet": "LOCAL",
    }
    data.update(overrides)
    return DicomConfiguration(**data)


def test_calling_aet_title_defaults_without_calling_aets() -> None:
    config = _base_config(calling_aet="LOCAL")
    assert config.calling_aet_title == "LOCAL"


def test_calling_aet_title_resolves_by_name() -> None:
    config = _base_config(
        calling_aet="primary",
        calling_aets={
            "primary": {
                "ae_title": "MCPSCU",
                "description": "Primary caller",
            }
        },
    )
    assert config.calling_aet_title == "MCPSCU"


def test_calling_aet_title_resolves_by_alias() -> None:
    config = _base_config(
        calling_aet="alias1",
        calling_aets={
            "primary": {
                "ae_title": "MCPSCU",
                "aliases": ["alias1"],
            }
        },
    )
    assert config.calling_aet_title == "MCPSCU"


def test_calling_aet_title_resolves_by_ae_title() -> None:
    config = _base_config(
        calling_aet="MCPSCU",
        calling_aets={
            "primary": {
                "ae_title": "MCPSCU",
                "aliases": ["alias1"],
            }
        },
    )
    assert config.calling_aet_title == "MCPSCU"


def test_resolve_calling_aet_unknown_raises() -> None:
    config = _base_config(
        calling_aet="primary",
        calling_aets={
            "primary": {
                "ae_title": "MCPSCU",
            }
        },
    )

    with pytest.raises(ValueError):
        config.resolve_calling_aet("missing")


def test_calling_aet_validation_rejects_unknown() -> None:
    with pytest.raises(
        ValidationError,
        match=r"Available calling_aets: primary \(ae_title=MCPSCU\)",
    ):
        _base_config(
            calling_aet="missing",
            calling_aets={
                "primary": {
                    "ae_title": "MCPSCU",
                }
            },
        )


def test_calling_aet_validation_lists_options_deterministically() -> None:
    with pytest.raises(ValidationError) as exc_info:
        _base_config(
            calling_aet="missing",
            calling_aets={
                "zeta": {
                    "ae_title": "ZETA",
                    "aliases": ["z-last", "z-first"],
                },
                "alpha": {
                    "ae_title": "ALPHA",
                    "aliases": ["b-alias", "a-alias"],
                },
            },
        )

    assert (
        "Available calling_aets: "
        "alpha (ae_title=ALPHA, aliases=a-alias, b-alias); "
        "zeta (ae_title=ZETA, aliases=z-first, z-last)"
    ) in str(exc_info.value)


def test_current_node_validation_lists_available_nodes() -> None:
    with pytest.raises(ValidationError, match="Available nodes: node1"):
        _base_config(current_node="missing")


def test_default_config_rejects_remote_hosts() -> None:
    with pytest.raises(
        ValidationError,
        match=r"Non-loopback DICOM hosts require allow_remote_hosts: true. Remote nodes: node1",
    ):
        _base_config(
            nodes={
                "node1": {
                    "host": "198.51.100.10",
                    "port": 11112,
                    "ae_title": "NODE",
                }
            }
        )


def test_default_config_allows_loopback_variants() -> None:
    for host in ("localhost", "127.0.0.1", "127.0.0.42", "::1", "[::1]"):
        config = _base_config(
            nodes={
                "node1": {
                    "host": host,
                    "port": 11112,
                    "ae_title": "NODE",
                }
            }
        )
        assert config.nodes["node1"].host == host


def test_remote_hosts_can_be_enabled_explicitly() -> None:
    config = _base_config(
        allow_remote_hosts=True,
        nodes={
            "node1": {
                "host": "pacs.example.internal",
                "port": 11112,
                "ae_title": "NODE",
            }
        },
    )
    assert config.allow_remote_hosts is True


def test_load_config_formats_validation_errors_for_humans(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "nodes": {
                    "orthanc": {
                        "host": "localhost",
                        "port": 4242,
                        "ae_title": "ORTHANC",
                    }
                },
                "current_node": "typo",
                "calling_aet": "MCPSCU",
            }
        )
    )

    with pytest.raises(
        DicomConfigurationError,
        match=r"Invalid configuration in .*Available nodes: orthanc",
    ):
        load_config(str(config_path))


def test_load_config_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("- not\n- a mapping\n")

    with pytest.raises(
        DicomConfigurationError,
        match=r"Invalid configuration in .*YAML must contain a mapping/object",
    ):
        load_config(str(config_path))


def test_load_config_wraps_yaml_parse_errors(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("nodes: [\n")

    with pytest.raises(
        DicomConfigurationError,
        match=r"Invalid configuration in .*bad.yaml",
    ):
        load_config(str(config_path))


def test_load_config_rejects_remote_hosts_without_opt_in(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "nodes": {
                    "remote": {
                        "host": "198.51.100.10",
                        "port": 104,
                        "ae_title": "REMOTE",
                    }
                },
                "current_node": "remote",
                "calling_aet": "MCPSCU",
            }
        )
    )

    with pytest.raises(
        DicomConfigurationError,
        match=r"allow_remote_hosts: true.*Remote nodes: remote",
    ):
        load_config(str(config_path))


def test_load_config_wraps_file_read_errors(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("nodes: {}\n")

    reader = mock_open()
    reader.side_effect = OSError("permission denied")
    monkeypatch.setattr("builtins.open", reader)

    with pytest.raises(
        DicomConfigurationError,
        match=r"Invalid configuration in .*permission denied",
    ):
        load_config(str(config_path))
