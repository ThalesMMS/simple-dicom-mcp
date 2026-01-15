"""
DICOM MCP Server main implementation.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List

from mcp.server.fastmcp import FastMCP

from .config import DicomConfiguration, load_config
from .dicom_client import DicomClient
from .errors import DicomError
from .server_prompt import register_prompts
from .server_tools_common import ToolDependencies
from .server_tools_core import register_core_tools
from .server_tools_queries import register_query_tools

# Configure logging
logger = logging.getLogger("dicom_mcp")


@dataclass
class DicomContext:
    """Context for the DICOM MCP server."""

    config: DicomConfiguration


def create_dicom_mcp_server(config_path: str, name: str = "DICOM MCP") -> FastMCP:
    """Create and configure a DICOM MCP server."""

    level_name = os.getenv("LOG_LEVEL")
    if level_name:
        level = getattr(logging, level_name.upper(), None)
        if isinstance(level, int):
            logger.setLevel(level)
            logging.getLogger("dicom_mcp.dicom_client").setLevel(level)

    def _create_client_from_config(config: DicomConfiguration) -> DicomClient:
        """Create a new DICOM client for the current configuration."""
        current_node = config.nodes[config.current_node]
        return DicomClient(
            host=current_node.host,
            port=current_node.port,
            calling_aet=config.calling_aet_title,
            called_aet=current_node.ae_title,
            query_root=config.query_root,
            network=config.network,
            node_name=config.current_node,
        )

    def _format_log_event(
        operation: str,
        config: DicomConfiguration | None = None,
        **fields: Any,
    ) -> str:
        base: Dict[str, Any] = {"operation": operation}
        if config is not None:
            current_node = config.nodes[config.current_node]
            base.update(
                {
                    "node": config.current_node,
                    "called_aet": current_node.ae_title,
                    "calling_aet": config.calling_aet_title,
                    "host": current_node.host,
                    "port": current_node.port,
                }
            )
        for key, value in fields.items():
            if value not in (None, "", [], {}):
                base[key] = value

        ordered_keys = ("operation", "node", "called_aet", "calling_aet", "host", "port")
        parts: List[str] = []
        for key in ordered_keys:
            value = base.get(key)
            if value not in (None, "", [], {}):
                parts.append(f"{key}={value}")
        extra_keys = [key for key in base.keys() if key not in ordered_keys]
        for key in sorted(extra_keys):
            value = base[key]
            if value in (None, "", [], {}):
                continue
            if isinstance(value, (list, tuple, set)):
                value = ",".join(str(item) for item in value)
            parts.append(f"{key}={value}")

        return "dicom_event " + " ".join(parts)

    def _error_payload(exc: Exception) -> Dict[str, Any]:
        if isinstance(exc, DicomError):
            return exc.to_dict()
        return {"type": exc.__class__.__name__, "message": str(exc)}

    def _tool_error_response(
        operation: str,
        config: DicomConfiguration | None,
        exc: Exception,
        base_payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        payload = dict(base_payload or {})
        error = _error_payload(exc)
        payload.setdefault("success", False)
        payload.setdefault("message", error.get("message", "Operation failed"))
        payload["error"] = error
        if sys.exc_info()[0] is not None:
            logger.exception(_format_log_event(operation, config, error=error.get("message")))
        else:
            logger.error(_format_log_event(operation, config, error=error.get("message")))
        return payload

    # Define a simple lifespan function
    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[DicomContext]:
        # Load config
        config = load_config(config_path)

        logger.info(_format_log_event("config_loaded", config))

        yield DicomContext(config=config)

    # Create server
    mcp = FastMCP(name, lifespan=lifespan)

    deps = ToolDependencies(
        create_client=_create_client_from_config,
        format_log_event=_format_log_event,
        tool_error_response=_tool_error_response,
    )

    register_core_tools(mcp, deps, server_name=name)
    register_query_tools(mcp, deps)
    register_prompts(mcp)

    return mcp
