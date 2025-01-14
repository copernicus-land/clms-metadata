import json
from pathlib import Path

import pytest
from pyjson5 import pyjson5

from clms_metadata.cli import odata

test_root = Path(__file__).parent.parent


@pytest.mark.parametrize(
    ("path", "reference_path"),
    [
        (  # ndvi_1km_v3_10daily
            test_root
            / "data/ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1.nc",
            test_root
            / "reference/ndvi_global_1km_10daily_v3/odata_c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1_nc.json5",
        ),
        (  # wl-rivers_vector_daily
            test_root
            / "data/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json",
            test_root
            / "reference/wl-rivers_global_vector_daily_v2/odata_c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json5",
        ),
    ],
)
def test_create(path: Path, reference_path: Path, tmp_path: Path):
    odata.create(str(path), output=tmp_path)
    [path_output] = [p for p in tmp_path.iterdir() if p.is_file()]
    with open(path_output) as f:
        output = json.load(f)
    with open(reference_path) as f:
        reference = pyjson5.load(f)

    for ignore in ("Link", "OriginDate"):
        assert ignore in output
        output.pop(ignore)
        reference.pop(ignore)

    assert output == reference
