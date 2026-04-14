"""
Main entry point for the DICOM MCP Server.
"""

import argparse
import logging
import os

from .config import load_config
from .errors import DicomConfigurationError
from .server import create_dicom_mcp_server


def _configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="level=%(levelname)s logger=%(name)s %(message)s",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="DICOM Model Context Protocol Server")
    parser.add_argument("config_path", help="Path to the DICOM configuration YAML file")
    parser.add_argument(
        "--transport",
        help="MCP transport type ('sse' or 'stdio')",
        default="stdio",
    )

    args = parser.parse_args()

    _configure_logging()

    try:
        config = load_config(args.config_path)
        mcp = create_dicom_mcp_server(config)
        mcp.run(args.transport)
    except DicomConfigurationError as exc:
        parser.exit(2, f"Configuration error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
