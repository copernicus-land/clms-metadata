from enum import Enum
from typing import Final

"""
Attribute names
"""


class Attributes(str, Enum):
    PROCESSING_CENTER = "processingCenter"
    AREA_OF_INTEREST = "areaOfInterest"
    DATASET_SHORT_NAME = "datasetShortName"
    DATASET_ALIAS = "datasetAlias"
    DATASET_VERSION = "datasetVersion"
    PRODUCT_VERSION = "productVersion"
    FILE_FORMAT = "fileFormat"
    TEMPORAL_REPEAT_RATE = "temporalRepeatRate"
    METRIC_GRID_SPACING = "metricGridSpacing"
    GRID_LABEL = "gridLabel"
    CONSOLIDATION_PERIOD = "consolidationPeriod"
    PLATFORM_SHORT_NAME = "platformShortName"
    PLATFORM_ACRONYM = "platformAcronym"
    INSTRUMENT_SHORT_NAME = "instrumentShortName"
    WATER_LEVEL_RIVER_NAME = "wlRiverName"
    WATER_LEVEL_LAKE_NAME = "wlLakeName"
    WATER_LEVEL_BASIN_NAME = "wlBasinName"
    MISSION_SHORT_NAME = "missionShortName"
    VPP_SEASON = "vppSeason"
    VPP_SUB_PARAMETER = "vppSubParameter"
    SWI_SUB_PARAMETER = "swiSubParameter"
    CELL_ID = "cellID"
    SDI_RESOURCE_IDENTIFIER = "SDIResourceIdentifier"
    COUNTRY_CODE = "countryCode"
    FUA_CODE = "fuaCode"
    FUA_NAME = "fuaName"
    PROJECTION_NAME = "projectionName"


"""
Attribute values
"""
UNSPECIFIED: Final[str] = "unspecified"
