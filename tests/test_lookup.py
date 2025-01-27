import pytest

from clms_metadata.source import lookup


@pytest.mark.parametrize(
    "filename, target",
    [
        ("c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1", "ndvi_global_1km_10daily_v3"),
        (
            "c_gls_DMP300-RT1_202408200000_GLOBE_OLCI_V1.1.1",
            "dmp_global_300m_10daily_v1",
        ),
        # clms_global_lswt_1km_v1_10daily-reproc_netcdf
        (
            "c_gls_LSWT_<unique>_GLOBE_AATSR_v1.0.2",
            "lswt-offline_global_1km_10daily_v1",
        ),
        # clms_global_lswt_1km_v1_10daily-nrt_netcdf
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRAB_v1.2.0", "lswt-nrt_global_1km_10daily_v1"),
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRAB_v1.1.0", "lswt-nrt_global_1km_10daily_v1"),
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRA_v1.0.2", "lswt-nrt_global_1km_10daily_v1"),
        ("c_gls_LSWT_<unique>_GLOBE_SLSTRA_v1.0.1", "lswt-nrt_global_1km_10daily_v1"),
        # clms_global_lwq_300m_v1_10daily-nrt_netcdf
        ("c_gls_LWQ300_<unique>_GLOBE_OLCI_V1.3.0", "lwq-nrt_global_300m_10daily_v1"),
        ("c_gls_LWQ300_<unique>_GLOBE_OLCI_V1.4.0", "lwq-nrt_global_300m_10daily_v1"),
        # clms_global_lwq_300m_v1_10daily-reproc_netcdf
        (
            "c_gls_LWQ300_<unique>_GLOBE_MERIS_V1.3.0",
            "lwq-reproc_global_300m_10daily_v1",
        ),
        # clms_global_lwq_100m_v1_10daily-nrt_netcdf
        ("c_gls_LWQ100_<unique>_GLOBAL_MSI_V1.3", "lwq-nrt_global_100m_10daily_v1"),
        ("c_gls_LWQ100_<unique>_GLOBAL_MSI_V1.5", "lwq-nrt_global_100m_10daily_v1"),
        # clms_global_lie_500m_v1_daily_netcdf
        (
            "c_gls_LIE-NH_<unique>_NHEMI_SLSTR_V1.2.0",
            "lie_northernhemisphere_500m_daily_v1",
        ),
        (
            "c_gls_LIE-NH_<unique>_NHEMI_SLSTR_V1.3.0",
            "lie_northernhemisphere_500m_daily_v1",
        ),
        (
            "c_gls_LIE-NH_<unique>_NHEMI_SLSTR_V1.1.1",
            "lie_northernhemisphere_500m_daily_v1",
        ),
        # clms_global_lie_250m_v1_daily_netcdf
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.2.1", "lie_baltic_250m_daily_v1"),
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.1.1", "lie_baltic_250m_daily_v1"),
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.0.1", "lie_baltic_250m_daily_v1"),
        ("c_gls_LIE250_<unique>_Baltic_MODIS_V1.2.2", "lie_baltic_250m_daily_v1"),
        # clms_global_sce_500m_v1_daily_netcdf
        ("c_gls_SCE500_<unique>_CEURO_MODIS_V1.0.1", "sce_europe_500m_daily_v1"),
        # clms_global_sce_1km_v1_daily_netcdf
        (
            "c_gls_SCE_<unique>_NHEMI_VIIRS_V1.0.1",
            "sce_northernhemisphere_1km_daily_v1",
        ),
        # clms_global_swe_5km_v1_daily_netcdf
        (
            "c_gls_SWE5K_<unique>_NHEMI_SSMIS_V1.0.2",
            "swe_northernhemisphere_5km_daily_v1",
        ),
        # clms_global_wb_100m_v1_monthly_netcdf
        ("c_gls_WB100_<unique>_GLOBE_S2_V1.0.1", "wb_global_100m_monthly_v1"),
        # clms_global_lie_250m_v2_daily_netcdf
        ("c_gls_LIE250_202402190000_CEURO_VIIRS_V2.2.1", "lie_europe_250m_daily_v2"),
        # no match
        ("c_gls_WB100_<unique>_LOBE_S2_V2.0.1", ValueError),
        (
            "c_gls_NDVI-STS_2015-2019-1211_GLOBE_PROBAV_V3.0.1",
            "ndvi-sts_global_1km_10daily_v3",
        ),
    ],
)
def test_extract_collection_id_from_cls_filename(filename, target):
    filename_with_date = filename.replace("<unique>", "201604210000")
    if isinstance(target, str):
        assert lookup.LookupSource.extract_collection_id(filename_with_date) == target
    else:
        with pytest.raises(target):
            lookup.LookupSource.extract_collection_id(filename_with_date)


@pytest.mark.parametrize(
    "collection_id, target",
    [
        ("ndvi_global_1km_10daily_v3", "vegetation_indices"),
        ("dmp_global_300m_10daily_v1", "dry-gross_dry_matter_productivity"),
        ("sce_europe_500m_daily_v1", "snow_cover_extent"),
        ("sce_northernhemisphere_1km_daily_v1", "snow_cover_extent"),
        ("swe_northernhemisphere_5km_daily_v1", "snow_water_equivalent"),
        ("lswt-nrt_global_1km_10daily_v1", "land_surface_temperature"),
        ("lswt-offline_global_1km_10daily_v1", "land_surface_temperature"),
        ("wb_global_100m_monthly_v1", "water_bodies"),
        ("wb_global_300m_monthly_v2", "water_bodies"),
        ("lwq-nrt_global_100m_10daily_v1", "lake_water_quality"),
        ("lwq-reproc_global_300m_10daily_v1", "lake_water_quality"),
        ("lwq-nrt_global_300m_10daily_v1", "lake_water_quality"),
        ("lie_baltic_250m_daily_v1", "river_and_lake_ice_extent"),
        ("lie_northernhemisphere_500m_daily_v1", "river_and_lake_ice_extent"),
        # no match
        ("w_something_else", None),
    ],
)
def test_determine_product_type(collection_id, target):
    assert lookup.LookupSource.determine_product_type(collection_id) == target
