from pathlib import Path

import pytest

from clms_metadata.source.path import get_common_name


@pytest.mark.parametrize(
    ("paths", "expected_name"),
    [
        (
            [
                Path("c_gls_DMP300-QFLAG-RT1_202408200000_GLOBE_OLCI_V1.1.1.tiff"),
                Path("c_gls_DMP300-DMP-RT1_202408200000_GLOBE_OLCI_V1.1.1.tiff"),
            ],
            "c_gls_DMP300-RT1_202408200000_GLOBE_OLCI_V1.1.1",
        ),
        (
            [
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Bare-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_BuiltUp-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Change-Confidence-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Crops-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_DataDensityIndicator_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-proba_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Forest-Type-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Grass-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_MossLichen-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_PermanentWater-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_SeasonalWater-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Shrub-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Snow-CoverFraction-layer_EPSG-4326.tif"
                ),
                Path(
                    "PROBAV_LC100_global_v3.0.1_2019-nrt_Tree-CoverFraction-layer_EPSG-4326.tif"
                ),
            ],
            "PROBAV_LC100_global_v3.0.1_2019",
        ),
        (
            [
                Path("c_gls_NDVI300-NDVI_201401010000_GLOBE_PROBAV_V1.0.1.tiff"),
            ],
            "c_gls_NDVI300_201401010000_GLOBE_PROBAV_V1.0.1",
        ),
        (
            [
                Path("c_gls_BA300-DOB-NTC_201901010000_GLOBE_S3_V3.1.1.tiff"),
            ],
            "c_gls_BA300-NTC_201901010000_GLOBE_S3_V3.1.1",
        ),
        (
            [
                Path("c_gls_BA300-DOB-NRT_202307010000_GLOBE_S3_V3.1.1.tiff"),
            ],
            "c_gls_BA300-NRT_202307010000_GLOBE_S3_V3.1.1",
        ),
        (
            [
                Path("c_gls_BA300_202307010000_GLOBE_S3_V3.1.1.tiff"),
            ],
            "c_gls_BA300_202307010000_GLOBE_S3_V3.1.1",
        ),
    ],
)
def test_get_common_name(paths, expected_name):
    assert get_common_name(paths) == expected_name
