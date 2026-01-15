"""
Prompt registrations for the MCP server.
"""

from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register MCP prompts."""

    @mcp.prompt()
    def dicom_query_guide() -> str:
        """Prompt for guiding users on how to query DICOM data."""
        return """
DICOM Query Guide

This DICOM Model Context Protocol (MCP) server allows you to interact with medical imaging data from DICOM nodes.

## Node Management
1. View available DICOM nodes and calling AE titles:
   ```
   list_dicom_nodes()
   ```

2. Switch to a different remote node (required to c-echoing and querying other nodes):
   ```
   switch_dicom_node(node_name="research")
   ```

3. Verify the connection to the remote node:
   ```
   verify_connection()
   ```

## Search Queries
For flexible search operations:

1. Search for patients:
   ```
   query_patients(patient_id="12345678")
   ```

2. Search for studies:
   ```
   query_studies(patient_id="12345678", study_date="20230101-20231231")
   ```

3. Search for series:
   ```
   query_series(study_instance_uid="1.2.840.10008.5.1.4.1.1.2.1.1", modality="CT")
   ```

4. Search for instances:
   ```
   query_instances(series_instance_uid="1.2.840.10008.5.1.4.1.1.2.1.2")
   ```

Query tools return a structured response:
```
{
  "success": true,
  "results": [],
  "dicom_statuses": [],
  "warnings": [],
  "error": null
}
```

## Attribute Presets
For all queries, you can specify an attribute preset:
- `none`: No attributes, use with additional_attributes (default)
- `custom`: Our custom attributes

Query specific tags (default behavior):
```
query_studies(patient_id="12345678", additional_attributes=["StudyInstanceUID", "StudyDate"])
```

Use custom preset for predefined attributes:
```
query_studies(patient_id="12345678", attribute_preset="custom")
```

You can also customize the custom preset:
```
query_studies(
    patient_id="12345678",
    attribute_preset="custom",
    additional_attributes=["StudyComments"],
    exclude_attributes=["AccessionNumber"]
)
```

To view available attribute presets:
```
get_attribute_presets()
```
"""
