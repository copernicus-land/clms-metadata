import re
from typing import Final

CONSOLIDATION: Final[re.Pattern] = re.compile(r"-RT(\d)_")
SENTINEL_OR_METOP: Final[re.Pattern] = re.compile(r"(SENTINEL\d+)|(METOP)")
SENTINEL_NUM_SERIAL: Final[re.Pattern] = re.compile(r"(SENTINEL)-?(\d+)([A-Z]+)")
SENTINEL_SHORT_NUM_SERIAL: Final[re.Pattern] = re.compile(r"(S)(\d+)([A-Z]+)")
SENTINEL_WITH_SPACE: Final[re.Pattern] = re.compile(r"(SENTINEL)\s+([0-9A-Z]+)")
NAME_WITH_SHORT_NAME_IN_BRACKETS: Final[re.Pattern] = re.compile(r"[\w ]+ \((\w+)\)")
SENSOR_SPOT_VEGETATION: Final[re.Pattern] = re.compile(r"(VEGETATION)-\d+")
SENSOR_SENTINEL1_SAR: Final[re.Pattern] = re.compile(r"C-?SAR")
SENSOR_SENTINEL3_SLSTR: Final[re.Pattern] = re.compile(r"(SLSTR)[A-Z]+")
MSG: Final[re.Pattern] = re.compile(r"(MSG)(\d+)")
GOES: Final[re.Pattern] = re.compile(r"(GOES)(?:(\d+)|E|R)")
METOP: Final[re.Pattern] = re.compile(r"(METOP)[ -]?([A-Z])")
PLATFORM_SERIALS_AND: Final[re.Pattern] = re.compile(r"\(([A-Z]) AND ([A-Z])\)")
RESOLUTION: Final[re.Pattern] = re.compile(r"_(([\d.]+)(m|km))_")
VERSION_DOTTED: Final[re.Pattern] = re.compile(r"v(\d)\.\d(:?\.\d)?")
VERSION_DIGITS_ONLY: Final[re.Pattern] = re.compile(r"v(\d)\d{2}")
VERSION_Vxx_Rxx: Final[re.Pattern] = re.compile(r"v(\d\d)_r(\d\d)")

DATASET_NDVI_STATISTICS: Final[re.Pattern] = re.compile(r"ndvi-(sts|lts)_")
DATASET_SWI_STATIC: Final[re.Pattern] = re.compile(r"swi-static")
DATASET_SWI_TIMESERIES: Final[re.Pattern] = re.compile(r"swi-timeseries")
DATASET_CLMS_PREFIX: Final[re.Pattern] = re.compile(
    r"clms_(?P<product_family>\w+)_(?P<descriptive_name>[\w\-]+)_(?P<spatial_extent>\w+)_(?P<resolution>\d+(:?m|km))_(?P<temporal_grid>\w+)_v(?P<version_major>\d)"
)

# Date
DATETIME_DIGITS_MINUTES: Final[re.Pattern] = re.compile(r"\d{12}")
"""
Regex for date format YYYYMMDDhhmm (12 digits)
"""

DATETIME_DIGITS_SECONDS: Final[re.Pattern] = re.compile(r"\d{14}")
"""
Regex for date format YYYYMMDDhhmmss (14 digits)
"""

DATE_YEAR1_YEAR2: Final[re.Pattern] = re.compile(r"\d{4}----\d{4}")
"""
Regex for date format YEAR1----YEAR2 (4 digits, 4 hyphens, 4 digits)
"""

DATE_YEAR1_YEAR2_MMDD: Final[re.Pattern] = re.compile(r"\d{4}-\d{4}-\d{4}")
"""
Regex for date format YEAR1-YEAR2-MMDD (4 digits, hyphen, 4 digits, hyphen, 4 digits)
"""

DATE_VLCC_S: Final[re.Pattern] = re.compile(r"_S(\d{4})_")

DATE_VLCC_C: Final[re.Pattern] = re.compile(r"_C(\d{4})-(\d{4})_")

DATE_VLCC_P: Final[re.Pattern] = re.compile(r"_P(\d{4})-(\d{4})_")


SWI_STATIC: Final[re.Pattern] = re.compile(
    r"c_gls_SWI-STATIC-(?P<swiSubParameter>[A-Z]+)_[\d-]{12}_GLOBE_[A-Z-0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
)
SWI_TIMESERIES: Final[re.Pattern] = re.compile(
    r"c_gls_SWI-TS_\d{12}_(?P<cellID>C\d{4})+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
)
LC100: Final[re.Pattern] = re.compile(
    r"(?:(?P<tile>[A-Za-z\d]+)_)?"  # optional tile
    r"(?P<sensor>[A-Za-z]+)"
    r"_"
    r"LC(?P<resolution>\d+)"
    r"_"
    r"global"
    r"_"
    r"v(?P<version>(?P<version_major>\d)\.\d\.\d)"
    r"_"
    r"(?P<year>\d{4})"
)

LSP: Final[re.Pattern] = re.compile(
    r"c_gls_LSP300-(?P<vppSubParameter>\w+)-(?P<vppSeason>S\d)_\d{12}_GLOBE_[A-Z-0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
)
TOC: Final[re.Pattern] = re.compile(
    r"cgl_TOC_\d{14}_(?P<cellID>X\d{2}Y\d{2})_\w+_v(?P<version>(?P<version_major>\d)\.\d\.\d)"
)
LCFM: Final[re.Pattern] = re.compile(
    r"LCFM_(?P<product_type>[\w-]+)_V\d{3}_(?P<year>\d{4})_(?P<cellID>[NS]\d{2}[EW]\d{3})"
)

LST10_DAILY_CYCLE: Final[re.Pattern] = re.compile(
    r"(?P<prefix>c_gls_LST10-DC)(-(?P<band>\w+))?_(?P<date>\d{8})(?P<time>\d{4})_GLOBE_GEO_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
)
