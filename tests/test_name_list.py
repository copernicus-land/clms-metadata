import pytest

import clms_metadata.constants.attributes as attributes
from clms_metadata.models.name_list import EOAssetNameList


@pytest.mark.parametrize(
    ("lookup", "expected"),
    [
        (
            dict(instrument="OLCI"),
            {
                attributes.MISSION_SHORT_NAME: "SENTINEL3",
                attributes.INSTRUMENT_SHORT_NAME: "OLCI",
            },
        ),
        (
            dict(mission="PROBAV"),
            {
                attributes.MISSION_SHORT_NAME: "PROBAV",
                attributes.PLATFORM_SHORT_NAME: "PROBAV",
                attributes.PLATFORM_ACRONYM: "PROBAV",
                attributes.INSTRUMENT_SHORT_NAME: "VEGETATION",
            },
        ),
    ],
)
def test_lookup(lookup: dict, expected: dict, eo_asset_name_list: EOAssetNameList):
    assert eo_asset_name_list.lookup(**lookup) == expected
