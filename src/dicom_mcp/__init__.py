"""
DICOM Model Context Protocol Server

A Model Context Protocol implementation for interacting with DICOM servers.
"""

from importlib.metadata import PackageNotFoundError, version

from .server import create_dicom_mcp_server

try:
    __version__ = version("simple-dicom-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0"
__all__ = ["create_dicom_mcp_server"]
