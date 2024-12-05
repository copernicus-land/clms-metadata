import pytest
from clms_metadata.source.lookup import bleh

@pytest.mark.parametrize(
    ("filename, target"),
    [
        ("c_gls_LSWT_<unique>_GLOBE_AATSR_v1.0.2", "lswt-offline_global_1km_10daily_v1"),  # clms_global_lswt_1km_v1_10daily-reproc_netcdf
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRAB_v1.2.0", "lswt-nrt_global_1km_10daily_v1"),  # clms_global_lswt_1km_v1_10daily-nrt_netcdf
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRAB_v1.1.0", "lswt-nrt_global_1km_10daily_v1"),  # clms_global_lswt_1km_v1_10daily-nrt_netcdf
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRA_v1.0.2", "lswt-nrt_global_1km_10daily_v1"),  # clms_global_lswt_1km_v1_10daily-nrt_netcdf
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRA_v1.0.1", "lswt-nrt_global_1km_10daily_v1"),  # clms_global_lswt_1km_v1_10daily-nrt_netcdf
        ("c_gls_LWQ300_<unique>_GLOBE_OLCI_V1.3.0", "lwq-nrt_global_300m_10daily_v1"),  # clms_global_lwq_300m_v1_10daily-nrt_netcdf
        ("c_gls_LWQ300_<unique>_GLOBE_OLCI_V1.4.0", "lwq-nrt_global_300m_10daily_v1"),  # clms_global_lwq_300m_v1_10daily-nrt_netcdf
        ("c_gls_LWQ300_<unique>_GLOBE_MERIS_V1.3.0", "lwq-reproc_global_300m_10daily_v1"),  # clms_global_lwq_300m_v1_10daily-reproc_netcdf
        ("c_gls_LWQ100_<unique>_GLOBAL_MSI_V1.3", "lwq-nrt_global_100m_10daily_v1"),  # clms_global_lwq_100m_v1_10daily-nrt_netcdf
        ("c_gls_LWQ100_<unique>_GLOBAL_MSI_V1.5", "lwq-nrt_global_100m_10daily_v1"),  # clms_global_lwq_100m_v1_10daily-nrt_netcdf
        ("c_gls_LIE-NH_<unique>_NHEMI_SLSTR_V1.2.0", "lie_northernhemisphere_500m_daily_v1"),  # clms_global_lie_500m_v1_daily_netcdf
        ("c_gls_LIE-NH_<unique>_NHEMI_SLSTR_V1.3.0", "lie_northernhemisphere_500m_daily_v1"),  # clms_global_lie_500m_v1_daily_netcdf
        ("c_gls_LIE-NH_<unique>_NHEMI_SLSTR_V1.1.1", "lie_northernhemisphere_500m_daily_v1"),  # clms_global_lie_500m_v1_daily_netcdf
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.2.1", "lie_baltic_250m_daily_v1"),  # clms_global_lie_250m_v1_daily_netcdf
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.1.1", "lie_baltic_250m_daily_v1"),  # clms_global_lie_250m_v1_daily_netcdf
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.0.1", "lie_baltic_250m_daily_v1"),  # clms_global_lie_250m_v1_daily_netcdf
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.2.2", "lie_baltic_250m_daily_v1"),  # clms_global_lie_250m_v1_daily_netcdf
        ("c_gls_SCE500_<unique>_CEURO_MODIS_V1.0.1", "sce_europe_500m_daily_v1"),  # clms_global_sce_500m_v1_daily_netcdf
        ("c_gls_SCE_<unique>_NHEMI_VIIRS_V1.0.1", "sce_northernhemisphere_1km_daily_v1"),  # clms_global_sce_1km_v1_daily_netcdf
        ("c_gls_SWE5K_<unique>_NHEMI_SSMIS_V1.0.2", "swe_northernhemisphere_5km_daily_v1"),  # clms_global_swe_5km_v1_daily_netcdf
        ("c_gls_WB100_<unique>_GLOBE_S2_V1.0.1", "wb_global_100m_monthly_v1"),  # clms_global_wb_100m_v1_monthly_netcdf
        ("c_gls_WB300_<unique>_GLOBE_S2_V2.0.1", "wb_global_300m_monthly_v2"),  # clms_global_wb_300m_v2_monthly_netcdf
    ]
)
def test_collection_from_cls_filename(filename, target):
    filename_with_date = filename.replace('<unique>', '201604210000')