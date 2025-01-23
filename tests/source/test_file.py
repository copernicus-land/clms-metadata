import pytest

from clms_metadata.source.file import (
    get_dataset_identifier_from_identifier_tag,
    parse_platform,
    parse_sensor,
)


@pytest.mark.parametrize(
    ("platformstr", "expected"),
    [
        ("Proba-V", {"PROBAV": ["PROBAV"]}),
        ("SPOT-4", {"SPOT4": ["SPOT4"]}),
        ("METOP A+B", {"METOP": ["METOPA", "METOPB"]}),
        ("Sentinel-1 A+B", {"SENTINEL1": ["SENTINEL1A", "SENTINEL1B"]}),
        ("Sentinel-3A", {"SENTINEL3": ["SENTINEL3A"]}),
        (
            "METOP A+B, Sentinel-1 A+B",
            {"METOP": ["METOPA", "METOPB"], "SENTINEL1": ["SENTINEL1A", "SENTINEL1B"]},
        ),
        ("SENTINEL-3A AND SENTINEL-3B", {"SENTINEL3": ["SENTINEL3A", "SENTINEL3B"]}),
        ("SENTINEL3A AND SENTINEL3B", {"SENTINEL3": ["SENTINEL3A", "SENTINEL3B"]}),
        ("TERRA (EOS AM-1)", {"TERRA": ["TERRA"]}),
        ("NOAA-20 (JPSS-1)", {"NOAA20": ["NOAA20"]}),
        (
            "GOES, MSG, HIMAWARI",
            {"GOES": None, "MSG": None, "HIMAWARI": None},
        ),  # eg. lst_5km_v1_10daily-daily-cycle: c_gls_LST10-DC_201710210000_GLOBE_GEO_V1.2.1
        (
            "GOES, MSG, MTSAT",
            {"GOES": None, "MSG": None, "MTSAT": None},
        ),  # eg. lst_5km_v1_hourly: c_gls_LST_201303192300_GLOBE_GEO_V1.2.1
        (
            "HIMAWARI8, GOES16, MSG4",
            {
                "HIMAWARI8": ["HIMAWARI8"],
                "GOES": ["GOES16"],
                "METEOSAT11": ["METEOSAT11"],
            },
        ),  # eg. lst_5km_v1_hourly: c_gls_LST_202101180500_GLOBE_GEO_V1.2.1
        (
            "METOP B+C",
            {"METOP": ["METOPB", "METOPC"]},
        ),  # eg. swi_12.5km_v3_10daily: c_gls_SWI10_202206111200_GLOBE_ASCAT_V3.2.1
        (
            "HIMAWARI8, GOES16, MSG2, MSG1",
            {
                "HIMAWARI8": ["HIMAWARI8"],
                "GOES": ["GOES16"],
                "METEOSAT9": ["METEOSAT9"],
                "METEOSAT8": ["METEOSAT8"],
            },
        ),  # eg. lst_5km_v2_hourly: c_gls_LST_202112192300_GLOBE_GEO_V2.0.1
        (
            "MetOp-A",
            {"METOP": ["METOPA"]},
        ),  # eg. swi_12.5km_v3_static: c_gls_SWI-STATIC-FM_201501010000_GLOBE_ASCAT_V1.1.1
        (
            "HIMAWARI9, GOES16, MSG4, MSG2",
            {
                "HIMAWARI9": ["HIMAWARI9"],
                "GOES": ["GOES16"],
                "METEOSAT11": ["METEOSAT11"],
                "METEOSAT9": ["METEOSAT9"],
            },
        ),
        (
            "METOP A",
            {"METOP": ["METOPA"]},
        ),  # eg. swi_12.5km_v3_10daily: c_gls_SWI10_201204211200_GLOBE_ASCAT_V3.1.1
        (
            "DMSP, Suomi NPP",
            {"DMSP": None, "SUOMI NPP": ["NPP"]},
        ),  # eg. swe_5km_v2_daily: c_gls_SWE5K_202408200000_NHEMI_SSMIS_V2.0.1
        (
            "SPOT-4, SPOT-5, Proba-V",
            {"SPOT4": ["SPOT4"], "SPOT5": ["SPOT5"], "PROBAV": ["PROBAV"]},
        ),  # eg. ndvi_1km_v3_statistics: c_gls_NDVI-LTS_1999-2019-0521_GLOBE_VGT-PROBAV_V3.0.1
        (
            "Terra (EOS AM-1)",
            {"TERRA": ["TERRA"]},
        ),  # eg. lie_250m_v1_daily: c_gls_LIE250_201704230000_Baltic_MODIS_V1.0.1
        (
            "Sentinel-3",
            {"SENTINEL3": None},
        ),  # eg. fapar_300m_v1_10daily: c_gls_FAPAR300-RT1_202103100000_GLOBE_OLCI_V1.1.1
        (
            "ENVISAT",
            {"ENVISAT": ["ENVISAT"]},
        ),  # eg. lwq_300m_v1_10daily-reproc: c_gls_LWQ300_200309210000_GLOBE_MERIS_V1.3.0
        (
            "Sentinel-2",
            {"SENTINEL2": None},
        ),  # lwq_100m_v1_10daily-nrt: c_gls_LWQ100_202401210000_GLOBAL_MSI_V1.5
        (
            "PLATFORM",
            {},
        ),  # eg. lwq_300m_v1_10daily-nrt: c_gls_LWQ300_202010010000_GLOBE_OLCI_V1.4.0
        (
            "Sentinel-2A",
            {"SENTINEL2": ["SENTINEL2A"]},
        ),  # eg. lwq_100m_v1_10daily-nrt: c_gls_LWQ100_201812210000_GLOBAL_MSI_V1.3
        (
            "MetOp-A, MetOp-B, GLDAS-NOAH",
            {"METOP": ["METOPA", "METOPB"]},  # TODO: what about GLDAS-NOAH?
        ),  # eg. swi_12.5km_v3_static: c_gls_SWI-STATIC-CI_201001010000_GLOBE_SWI-GLDAS_V1.1.1
        (
            "GOESR,  MSG4,  MSG1,  HIMAWARI8",
            {
                "GOES": ["GOESR"],
                "METEOSAT11": ["METEOSAT11"],
                "METEOSAT8": ["METEOSAT8"],
                "HIMAWARI8": ["HIMAWARI8"],
            },
        ),  # eg. lst_5km_v2_10daily-tci: c_gls_LST10-TCI-MIN_202101110000_GLOBE_GEO_V2.1.1
        (
            "N/A",
            {},
        ),  # eg. swi_12.5km_v3_static c_gls_SWI-STATIC-TC_201501010000_GLOBE_GTOPO30_V1.1.1
    ],
)
def test_get_platform(platformstr, expected):
    assert parse_platform(platformstr) == expected


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
def test_parse_sensor(sensor_tag: str, expected: list[str]):
    assert parse_sensor(sensor_tag) == expected
