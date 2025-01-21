import re
from typing import Final

CONSOLIDATION: Final[re.Pattern] = re.compile(r"-RT(\d)_")
SENTINEL_OR_METOP: Final[re.Pattern] = re.compile(r"(SENTINEL\d+)|(METOP)")
SENTINEL_NUM_SERIAL: Final[re.Pattern] = re.compile(r"(SENTINEL)-?(\d+)([A-Z]+)")
NAME_WITH_SHORT_NAME_IN_BRACKETS: Final[re.Pattern] = re.compile(r"[\w ]+ \((\w+)\)")
SENSOR_SPOT_VEGETATION: Final[re.Pattern] = re.compile(r"(VEGETATION)-\d+")
SENSOR_SENTINEL3_SLSTR: Final[re.Pattern] = re.compile(r"(SLSTR)[A-Z]+")
MSG: Final[re.Pattern] = re.compile(r"(MSG)(\d+)")
GOES: Final[re.Pattern] = re.compile(r"(GOES)(\d+|E|R)")
METOP: Final[re.Pattern] = re.compile(r"(METOP)[ -]?([A-Z])")
PLATFORM_SERIALS_AND: Final[re.Pattern] = re.compile(r"\(([A-Z]) AND ([A-Z])\)")
RESOLUTION: Final[re.Pattern] = re.compile(r"_(([\d.]+)(m|km))_")


# Date
DATETIME_DIGITS: Final[re.Pattern] = re.compile(r"\d{12}")
"""
Regex for date format YYYYMMDDhhmm (12 digits)
"""

DATE_YEAR1_YEAR2: Final[re.Pattern] = re.compile(r"\d{4}----\d{4}")
"""
Regex for date format YEAR1----YEAR2 (4 digits, 4 hyphens, 4 digits)
"""

DATE_YEAR1_YEAR2_MMDD: Final[re.Pattern] = re.compile(r"\d{4}-\d{4}-\d{4}")
"""
Regex for date format YEAR1-YEAR2-MMDD (4 digits, hyphen, 4 digits, hyphen, 4 digits)
"""
