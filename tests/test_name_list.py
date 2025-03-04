import pytest
from conftest import assert_dict_subset

from clms_metadata.models.name_list import (
    EOAssetNameList,
    Instrument,
    Mission,
    Platform,
    autocomplete,
    get_common,
)


@pytest.mark.parametrize(
    ("lookup", "expected"),
    [
        (
            dict(instrument="OLCI"),
            {"missionShortName": "SENTINEL3", "instrumentShortName": "OLCI"},
        ),
        (
            dict(mission="PROBAV"),
            {
                "missionShortName": "PROBAV",
                "platformShortName": "PROBAV",
                "platformAcronym": "PROBAV",
                "instrumentShortName": "VEGETATION",
            },
        ),
        (
            dict(mission="SENTINEL2"),
            {"missionShortName": "SENTINEL2", "instrumentShortName": "MSI"},
        ),
    ],
)
def test_lookup(lookup: dict, expected: dict, eo_asset_name_list: EOAssetNameList):
    hits = list(eo_asset_name_list.lookup(**lookup))
    mission, platform, instrument = (get_common([h[i] for h in hits]) for i in range(3))

    if "missionShortName" in expected:
        assert mission.missionShortName == expected["missionShortName"]
    if "platformShortName" in expected:
        assert platform.platformShortName == expected["platformShortName"]
    if "platformAcronym" in expected:
        assert platform.platformAcronym == expected["platformAcronym"]
    if "instrumentShortName" in expected:
        assert instrument.instrumentShortName == expected["instrumentShortName"]


@pytest.mark.parametrize(
    ("missions", "instrument_short_names", "expected"),
    [
        (
            [Mission()],
            ["OLCI"],
            [
                Mission(
                    missionShortName="SENTINEL3",
                    platforms=[
                        Platform(instruments=[Instrument(instrumentShortName="OLCI")])
                    ],
                )
            ],
        ),
    ],
)
def test_autocomplete(
    missions: list[Mission],
    instrument_short_names: list[str],
    expected: list[Mission],
    eo_asset_name_list: EOAssetNameList,
):
    autocomplete(missions, instrument_short_names, eo_asset_name_list)
    for i in range(len(expected)):
        assert_dict_subset(
            expected[i].model_dump(exclude_none=True),
            missions[i].model_dump(exclude_none=True),
        )
