import pytest
from conftest import assert_dict_subset

from clms_metadata.models.name_list import (
    EOAssetNameList,
    Mission,
    Platform,
)
from clms_metadata.source.file import (
    get_dataset_identifier_from_identifier_tag,
    get_processing_center,
    parse_platform,
    parse_sensor,
)


@pytest.mark.parametrize(
    ("platformstr", "expected"),
    [
        (
            "Proba-V",
            [Mission(missionShortName="PROBAV")],
        ),
        (
            "SPOT-4",
            [Mission(missionShortName="SPOT4")],
        ),
        (
            "METOP A+B",
            [
                Mission(
                    missionShortName="METOP",
                    platforms=[
                        Platform(platformShortName="METOPA"),
                        Platform(platformShortName="METOPB"),
                    ],
                )
            ],
        ),
        (
            "Sentinel-1 A+B",
            [
                Mission(
                    missionShortName="SENTINEL1",
                    platforms=[
                        Platform(platformShortName="SENTINEL1A"),
                        Platform(platformShortName="SENTINEL1B"),
                    ],
                )
            ],
        ),
        (
            "Sentinel-3A",
            [
                Mission(
                    missionShortName="SENTINEL3",
                    platforms=[Platform(platformShortName="SENTINEL3A")],
                )
            ],
        ),
        (
            "METOP A+B, Sentinel-1 A+B",
            [
                Mission(
                    missionShortName="METOP",
                    platforms=[
                        Platform(platformShortName="METOPA"),
                        Platform(platformShortName="METOPB"),
                    ],
                ),
                Mission(
                    missionShortName="SENTINEL1",
                    platforms=[
                        Platform(platformShortName="SENTINEL1A"),
                        Platform(platformShortName="SENTINEL1B"),
                    ],
                ),
            ],
        ),
        (
            "SENTINEL-3A AND SENTINEL-3B",
            [
                Mission(
                    missionShortName="SENTINEL3",
                    platforms=[
                        Platform(platformShortName="SENTINEL3A"),
                        Platform(platformShortName="SENTINEL3B"),
                    ],
                )
            ],
        ),
        (
            "SENTINEL3A AND SENTINEL3B",
            [
                Mission(
                    missionShortName="SENTINEL3",
                    platforms=[
                        Platform(platformShortName="SENTINEL3A"),
                        Platform(platformShortName="SENTINEL3B"),
                    ],
                )
            ],
        ),
        (
            "TERRA (EOS AM-1)",
            [Mission(missionShortName="TERRA")],
        ),
        (
            "NOAA-20 (JPSS-1)",
            [Mission(missionShortName="NOAA20")],
        ),
        (
            "GOES, MSG, HIMAWARI",
            [Mission(missionShortName="GOES"), Mission()],
        ),  # eg. lst_5km_v1_10daily-daily-cycle: c_gls_LST10-DC_201710210000_GLOBE_GEO_V1.2.1
        (
            "GOES, MSG, MTSAT",
            [Mission(missionShortName="GOES"), Mission()],
        ),  # eg. lst_5km_v1_hourly: c_gls_LST_201303192300_GLOBE_GEO_V1.2.1
        (
            "HIMAWARI8, GOES16, MSG4",
            [
                Mission(
                    missionShortName="HIMAWARI8",
                ),
                Mission(
                    missionShortName="GOES",
                    platforms=[Platform(platformShortName="GOES16")],
                ),
                Mission(
                    missionShortName="METEOSAT11",
                    platforms=[Platform(platformShortName="METEOSAT11")],
                ),
            ],
        ),  # eg. lst_5km_v1_hourly: c_gls_LST_202101180500_GLOBE_GEO_V1.2.1
        (
            "METOP B+C",
            [
                Mission(
                    missionShortName="METOP",
                    platforms=[
                        Platform(platformShortName="METOPB"),
                        Platform(platformShortName="METOPC"),
                    ],
                )
            ],
        ),  # eg. swi_12.5km_v3_10daily: c_gls_SWI10_202206111200_GLOBE_ASCAT_V3.2.1
        (
            "HIMAWARI8, GOES16, MSG2, MSG1",
            [
                Mission(
                    missionShortName="HIMAWARI8",
                ),
                Mission(
                    missionShortName="GOES",
                    platforms=[Platform(platformShortName="GOES16")],
                ),
                Mission(
                    missionShortName="METEOSAT9",
                    platforms=[Platform(platformShortName="METEOSAT9")],
                ),
                Mission(
                    missionShortName="METEOSAT8",
                    platforms=[Platform(platformShortName="METEOSAT8")],
                ),
            ],
        ),  # eg. lst_5km_v2_hourly: c_gls_LST_202112192300_GLOBE_GEO_V2.0.1
        (
            "MetOp-A",
            [
                Mission(
                    missionShortName="METOP",
                    platforms=[Platform(platformShortName="METOPA")],
                )
            ],
        ),  # eg. swi_12.5km_v3_static: c_gls_SWI-STATIC-FM_201501010000_GLOBE_ASCAT_V1.1.1
        (
            "HIMAWARI9, GOES16, MSG4, MSG2",
            [
                Mission(
                    missionShortName="HIMAWARI9",
                ),
                Mission(
                    missionShortName="GOES",
                    platforms=[Platform(platformShortName="GOES16")],
                ),
                Mission(
                    missionShortName="METEOSAT11",
                    platforms=[Platform(platformShortName="METEOSAT11")],
                ),
                Mission(
                    missionShortName="METEOSAT9",
                    platforms=[Platform(platformShortName="METEOSAT9")],
                ),
            ],
        ),
        (
            "METOP A",
            [
                Mission(
                    missionShortName="METOP",
                    platforms=[Platform(platformShortName="METOPA")],
                )
            ],
        ),  # eg. swi_12.5km_v3_10daily: c_gls_SWI10_201204211200_GLOBE_ASCAT_V3.1.1
        (
            "DMSP, Suomi NPP",
            [
                Mission(
                    missionShortName="SUOMINPP",
                ),
                Mission(),
            ],
        ),  # eg. swe_5km_v2_daily: c_gls_SWE5K_202408200000_NHEMI_SSMIS_V2.0.1
        (
            "SPOT-4, SPOT-5, Proba-V",
            [
                Mission(
                    missionShortName="SPOT4",
                ),
                Mission(
                    missionShortName="SPOT5",
                ),
                Mission(
                    missionShortName="PROBAV",
                ),
            ],
        ),  # eg. ndvi_1km_v3_statistics: c_gls_NDVI-LTS_1999-2019-0521_GLOBE_VGT-PROBAV_V3.0.1
        (
            "Terra (EOS AM-1)",
            [
                Mission(
                    missionShortName="TERRA",
                )
            ],
        ),  # eg. lie_250m_v1_daily: c_gls_LIE250_201704230000_Baltic_MODIS_V1.0.1
        (
            "Sentinel-3",
            [Mission(missionShortName="SENTINEL3")],
        ),  # eg. fapar_300m_v1_10daily: c_gls_FAPAR300-RT1_202103100000_GLOBE_OLCI_V1.1.1
        (
            "ENVISAT",
            [
                Mission(
                    missionShortName="ENVISAT",
                )
            ],
        ),  # eg. lwq_300m_v1_10daily-reproc: c_gls_LWQ300_200309210000_GLOBE_MERIS_V1.3.0
        (
            "Sentinel-2",
            [Mission(missionShortName="SENTINEL2")],
        ),  # lwq_100m_v1_10daily-nrt: c_gls_LWQ100_202401210000_GLOBAL_MSI_V1.5
        (
            "PLATFORM",
            [Mission()],
        ),  # eg. lwq_300m_v1_10daily-nrt: c_gls_LWQ300_202010010000_GLOBE_OLCI_V1.4.0
        (
            "Sentinel-2A",
            [
                Mission(
                    missionShortName="SENTINEL2",
                    platforms=[Platform(platformShortName="SENTINEL2A")],
                )
            ],
        ),  # eg. lwq_100m_v1_10daily-nrt: c_gls_LWQ100_201812210000_GLOBAL_MSI_V1.3
        (
            "MetOp-A, MetOp-B, GLDAS-NOAH",
            [
                Mission(
                    missionShortName="METOP",
                    platforms=[
                        Platform(platformShortName="METOPA"),
                        Platform(platformShortName="METOPB"),
                    ],
                ),
                Mission(),
            ],
        ),  # eg. swi_12.5km_v3_static: c_gls_SWI-STATIC-CI_201001010000_GLOBE_SWI-GLDAS_V1.1.1
        (
            "GOESR,  MSG4,  MSG1,  HIMAWARI8",
            [
                Mission(missionShortName="GOES"),
                Mission(
                    missionShortName="METEOSAT11",
                    platforms=[Platform(platformShortName="METEOSAT11")],
                ),
                Mission(
                    missionShortName="METEOSAT8",
                    platforms=[Platform(platformShortName="METEOSAT8")],
                ),
                Mission(
                    missionShortName="HIMAWARI8",
                ),
            ],
        ),  # eg. lst_5km_v2_10daily-tci: c_gls_LST10-TCI-MIN_202101110000_GLOBE_GEO_V2.1.1
        (
            "N/A",
            [Mission()],
        ),  # eg. swi_12.5km_v3_static c_gls_SWI-STATIC-TC_201501010000_GLOBE_GTOPO30_V1.1.1
        (
            "S3A",
            [
                Mission(
                    missionShortName="SENTINEL3",
                    platforms=[Platform(platformShortName="SENTINEL3A")],
                )
            ],
        ),
    ],
)
def test_get_platform(platformstr, expected, eo_asset_name_list):
    assert_dict_subset(
        {m.missionShortName: m for m in expected},
        parse_platform(platformstr, eo_asset_name_list),
    )


@pytest.mark.parametrize(
    "identifier, expected",
    [
        (
            "urn:cgls:continents:sce500_v1_0.005degree:SCE500_201703010000_CEURO_MODIS_V1.0.1",
            "sce_europe_500m_daily_v1",
        ),
        (
            "urn:cgls:global:sce_v1_0.01degree:SCE_201801090000_NHEMI_VIIRS_V1.0.1",
            "sce_northernhemisphere_1km_daily_v1",
        ),
        (
            "urn:cgls:global:swe_V1_5km:SWE5K_200601010000_NHEMI_SSMIS_V1.0.2",
            "swe_northernhemisphere_5km_daily_v1",
        ),
        (
            "urn:cgls:global:wb_v1_100m:WB100_202010010000_GLOBE_S2_V1.0.1",
            "wb_global_100m_monthly_v1",
        ),
        (
            "urn:cgls:global:wb_v2_300m:WB300_202010010000_GLOBE_S2_V2.0.1",
            "wb_global_300m_monthly_v2",
        ),
        (
            "urn:cgls:global:lwq_v1_100:c_gls_LWQ100_201812210000_UTM_GLOBE_MSI_V1.3",
            "lwq-nrt_global_100m_10daily_v1",
        ),
        (
            "urn:cgls:continents:lie_v1_250m:LIE250_201703150000_Baltic_MODIS_V1.0.1",
            None,
        ),  # lie_vx_250m not unique to Baltic
        (
            "urn:cgls:continents:lie_v2_250m:LIE250_202402190000_CEURO_VIIRS_V2.2.1",
            None,
        ),  # lie_vx_250m not unique to CEURO
        (
            "urn:cgls:global:lie_nh_v1_500m:LIE-NH_202104010000_NHEMI_SLSTR_v1.1.1",
            "lie_northernhemisphere_500m_daily_v1",
        ),
        (
            "urn:cgls:global:fapar300_v1_333m:FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2",
            "fapar_global_300m_10daily_v1",
        ),
        (
            "urn:cgls:global:ndvi_v3_1km:NDVI_202004010000_GLOBE_PROBAV_V3.0.1",
            "ndvi_global_1km_10daily_v3",
        ),
        ("urn:cgls:global:not_in_mapping:LIE-NH_202104010000_NHEMI_SLSTR_V1.1.1", None),
        ("LIE-NH_202104010000_NHEMI_SLSTR_V1.1.1", None),
        (
            "urn:cgls:global:fcover_v2_1km:FCOVER-RT2_201909100000_GLOBE_PROBAV_V2.0.1",
            "fcover_global_1km_10daily_v2",
        ),
        (
            "urn:cgls:global:lst10-dc_v1_0.045degree:LST10-DC_201909010000_GLOBE_GEO_V1.2.1",
            "lst-daily-cycle_global_5km_10daily_v1",
        ),
        (
            "urn:cgls:global:lst_v2_0.045degree:LST_202501121100_GLOBE_GEO_V2.1.2",
            "lst_global_5km_hourly_v2",
        ),
        (
            "urn:cgls:global:ndvi300_v1_333m:NDVI300_201706010000_GLOBE_PROBAV_V1.0.1",
            "ndvi_global_300m_10daily_v1",
        ),
    ],
)
def test_get_dataset_identifier_from_identifier_tag(identifier, expected):
    assert get_dataset_identifier_from_identifier_tag(identifier) == expected


@pytest.mark.parametrize(
    ("sensor_tag", "expected"),
    [
        ("OLCI", ["OLCI"]),
        ("Visible Infrared Imaging Radiometer Suite (VIIRS)", ["VIIRS"]),
        ("SSMIS, VIIRS", ["SSMIS", "VIIRS"]),
        ("The Sea and Land Surface Temperature Radiometer (SLSTR)", ["SLSTR"]),
        ("Moderate Resolution Imaging Spectrometer (MODIS)", ["MODIS"]),
    ],
)
def test_parse_sensor(
    sensor_tag: str, expected: list[str], eo_asset_name_list: EOAssetNameList
):
    assert parse_sensor(sensor_tag, eo_asset_name_list=eo_asset_name_list) == expected


@pytest.mark.parametrize(
    ("institution_tag", "expected"),
    [
        ("VITO", "VITO"),
        ("vito", "VITO"),
        ("VITO NV", "VITO"),
        ("LEGOS, CLS, CNES", "CLS"),
        (
            "Brockmann Consult GmbH, Plymouth Marine Laboratory",
            "Brockmann Consult,Plymouth Marine Laboratory",
        ),
    ],
)
def test_get_processing_center(institution_tag: str, expected: str):
    assert get_processing_center({"institution": institution_tag}) == expected
