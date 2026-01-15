"""
DICOM Client.

This module provides a clean interface to pynetdicom functionality,
abstracting the details of DICOM networking.
"""

from .dicom_client_base import DicomClientBase
from .dicom_client_queries import DicomClientQueryMixin


class DicomClient(
    DicomClientBase,
    DicomClientQueryMixin,
):
    """DICOM networking client that handles communication with DICOM nodes."""

