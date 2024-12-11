import pytest

from clms_metadata.source.file import parse_platform


@pytest.mark.parametrize(
    ("platformstr", "expected"),
    [
        ("Proba-V", {"PROBA-V": None}),
        ("SPOT-4", {"SPOT-4": None}),
        ("METOP A+B", {"METOP": ["A", "B"]}),
        ("Sentinel-1 A+B", {"SENTINEL-1": ["A", "B"]}),
        ("Sentinel-3A", {"SENTINEL-3": ["A"]}),
        ("METOP A+B, Sentinel-1 A+B", {"METOP": ["A", "B"], "SENTINEL-1": ["A", "B"]}),
        ("SENTINEL-3A AND SENTINEL-3B", {"SENTINEL-3": ["A", "B"]}),
        ("SENTINEL3A AND SENTINEL3B", {"SENTINEL-3": ["A", "B"]}),
        ("TERRA (EOS AM-1)", {"TERRA": None}),
        ("NOAA-20 (JPSS-1)", {"NOAA-20": None}),
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
            {"HIMAWARI-8": None, "GOES-16": None, "MSG-4": None},
        ),  # eg. lst_5km_v1_hourly: c_gls_LST_202101180500_GLOBE_GEO_V1.2.1
        (
            "METOP B+C",
            {"METOP": ["B", "C"]},
        ),  # eg. swi_12.5km_v3_10daily: c_gls_SWI10_202206111200_GLOBE_ASCAT_V3.2.1
        (
            "HIMAWARI8, GOES16, MSG2, MSG1",
            {"HIMAWARI-8": None, "GOES-16": None, "MSG-2": None, "MSG-1": None},
        ),  # eg. lst_5km_v2_hourly: c_gls_LST_202112192300_GLOBE_GEO_V2.0.1
        (
            "MetOp-A",
            {"METOP": ["A"]},
        ),  # eg. swi_12.5km_v3_static: c_gls_SWI-STATIC-FM_201501010000_GLOBE_ASCAT_V1.1.1
        (
            "HIMAWARI9, GOES16, MSG4, MSG2",
            {"HIMAWARI-9": None, "GOES-16": None, "MSG-4": None, "MSG-2": None},
        ),
        (
            "METOP A",
            {"METOP": ["A"]},
        ),  # eg. swi_12.5km_v3_10daily: c_gls_SWI10_201204211200_GLOBE_ASCAT_V3.1.1
        (
            "DMSP, Suomi NPP",
            {"DMSP": None, "SUOMI NPP": None},
        ),  # eg. swe_5km_v2_daily: c_gls_SWE5K_202408200000_NHEMI_SSMIS_V2.0.1
        (
            "SPOT-4, SPOT-5, Proba-V",
            {"SPOT-4": None, "SPOT-5": None, "PROBA-V": None},
        ),  # eg. ndvi_1km_v3_statistics: c_gls_NDVI-LTS_1999-2019-0521_GLOBE_VGT-PROBAV_V3.0.1
        (
            "Terra (EOS AM-1)",
            {"TERRA": None},
        ),  # eg. lie_250m_v1_daily: c_gls_LIE250_201704230000_Baltic_MODIS_V1.0.1
        (
            "Sentinel-3",
            {"SENTINEL-3": None},
        ),  # eg. fapar_300m_v1_10daily: c_gls_FAPAR300-RT1_202103100000_GLOBE_OLCI_V1.1.1
        (
            "ENVISAT",
            {"ENVISAT": None},
        ),  # eg. lwq_300m_v1_10daily-reproc: c_gls_LWQ300_200309210000_GLOBE_MERIS_V1.3.0
        (
            "Sentinel-2",
            {"SENTINEL-2": None},
        ),  # lwq_100m_v1_10daily-nrt: c_gls_LWQ100_202401210000_GLOBAL_MSI_V1.5
        (
            "PLATFORM",
            {},
        ),  # eg. lwq_300m_v1_10daily-nrt: c_gls_LWQ300_202010010000_GLOBE_OLCI_V1.4.0
        (
            "Sentinel-2A",
            {"SENTINEL-2": ["A"]},
        ),  # eg. lwq_100m_v1_10daily-nrt: c_gls_LWQ100_201812210000_GLOBAL_MSI_V1.3
        (
            "MetOp-A, MetOp-B, GLDAS-NOAH",
            {"METOP": ["A", "B"], "GLDAS-NOAH": None},
        ),  # eg. swi_12.5km_v3_static: c_gls_SWI-STATIC-CI_201001010000_GLOBE_SWI-GLDAS_V1.1.1
        (
            "GOESR,  MSG4,  MSG1,  HIMAWARI8",
            {"GOES-R": None, "MSG-4": None, "MSG-1": None, "HIMAWARI-8": None},
        ),  # eg. lst_5km_v2_10daily-tci: c_gls_LST10-TCI-MIN_202101110000_GLOBE_GEO_V2.1.1
        (
            "N/A",
            {},
        ),  # eg. swi_12.5km_v3_static c_gls_SWI-STATIC-TC_201501010000_GLOBE_GTOPO30_V1.1.1
    ],
)
def test_get_platform(platformstr, expected):
    assert parse_platform(platformstr) == expected
