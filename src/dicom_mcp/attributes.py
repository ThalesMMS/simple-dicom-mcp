"""
DICOM attribute presets for different query levels.
"""

from typing import Dict, List, Optional

# Dictionary of attribute presets for each query level
ATTRIBUTE_PRESETS = {
    # No attributes - use with additional_attrs to query specific tags only
    "none": {
        "patient": [],
        "study": [],
        "series": [],
        "instance": [],
    },

    # Custom attribute set - our tailored attributes
    "custom": {
        "patient": [
            "PatientID",
            "PatientBirthDate",
            "PatientSex",
            "PatientAge",
        ],
        
        "study": [
            "StudyInstanceUID",
            "PatientID",
            "AccessionNumber",
            "StudyDescription",
            "PatientBirthDate",
            "PatientSex",
            "PatientAge",
            "StudyDate",
            "RequestedProcedureDescription",
            "RequestedProcedureCodeSequence",
        ],
        
        "series": [
            "SeriesInstanceUID",
            "StudyInstanceUID",
            "Modality",
            "SeriesDescription",
            "BodyPartExamined",
            "ProtocolName",
            "RequestAttributesSequence",
        ],
        
        "instance": [
            "SOPInstanceUID",
            "SeriesInstanceUID",
            ],
    },
}


def get_attributes_for_level(
    level: str, 
    preset: str = "none", 
    additional_attrs: Optional[List[str]] = None, 
    exclude_attrs: Optional[List[str]] = None
) -> List[str]:
    """Get the list of attributes for a specific query level and preset.

    Args:
        level: Query level (patient, study, series, instance)
        preset: Attribute preset name (none, custom).
                Defaults to "none" - caller must specify attributes via additional_attrs.
        additional_attrs: Additional attributes to include
        exclude_attrs: Attributes to exclude

    Returns:
        List of DICOM attribute names
    """
    # Start with the preset attributes
    if preset in ATTRIBUTE_PRESETS and level in ATTRIBUTE_PRESETS[preset]:
        attr_list = ATTRIBUTE_PRESETS[preset][level].copy()
    elif preset in ATTRIBUTE_PRESETS and level not in ATTRIBUTE_PRESETS[preset]:
        # If preset exists but doesn't have this level, fall back to none
        attr_list = ATTRIBUTE_PRESETS["none"][level].copy()
    else:
        # If preset doesn't exist, fall back to none
        attr_list = ATTRIBUTE_PRESETS["none"][level].copy()
    
    # Add additional attributes
    if additional_attrs:
        for attr in additional_attrs:
            if attr not in attr_list:
                attr_list.append(attr)
    
    # Remove excluded attributes
    if exclude_attrs:
        attr_list = [attr for attr in attr_list if attr not in exclude_attrs]
    
    return attr_list
