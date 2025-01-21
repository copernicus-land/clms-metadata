import re
from typing import Final

REGEX_CONSOLIDATION: Final[re.Pattern] = re.compile(r"-RT(\d)_")
