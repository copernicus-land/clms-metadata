from pathlib import Path
import shutil
import pytest
from pprint import pprint

import pytest

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import LinkSettings, Settings
from clms_metadata.storage import LocalFileSystem

test_data = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    ("name", "files", "suffix", "content_type", "platform", "instrument"),
    [
        (
            "c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1",
            (
                test_data
                / "ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1.nc",
            ),
            "nc",
            "application/netcdf",
            "PROBA-V",
            "VEGETATION",
        ),
        (
            "c_gls_NDVI_199901010000_GLOBE_VGT_V3.0.1",
            tuple(
                test_data
                / "ndvi_global_1km_10daily_v3"
                / f"c_gls_NDVI-{band}_199901010000_GLOBE_VGT_V3.0.1.tiff"
                for band in ("NDVI", "NOBS", "QFLAG", "TIMEGRID", "UNC")
            ),
            "cog",
            "application/tiff",
            "SPOT-4",
            "VEGETATION-1",
        ),
    ],
)
def test_ndvi_1km_v3_10daily(name, files, suffix, content_type, platform, instrument):
    assert all(p.exists() for p in files)

    builder = MetadataBuilder(
        storage=LocalFileSystem(), settings=Settings(link=LinkSettings(value="test"))
    )
    m = builder.build(files)
    assert m.name == name
    assert m.name_suffix == suffix
    assert m.content_type == content_type
    assert m.get_attribute("nominalResolutionMeters").value == 1000
    assert m.get_attribute("nominalResolution").value == "1km"
    assert m.get_attribute("platformShortName").value == platform
    assert m.get_attribute("instrumentShortName").value == instrument
    assert m.get_attribute("processingCenter").value == "VITO"
    assert m.product_type == "vegetation_indices"
    assert m.get_attribute("datasetIdentifier").value == "ndvi_global_1km_10daily_v3"
    assert m.get_attribute("datasetAlias").value == "ndvi_global_1km_10daily"
    assert m.get_attribute("collectionVersion").value == 3
    assert m.get_attribute("component").value == "bio-geophysical"
    assert m.get_attribute("fileFormat").value == suffix
    assert m.get_attribute("temporalGrid").value == "10-daily"


@pytest.mark.skip  # TODO: implement test for DMP
def test_dmp_300m_v1_10daily_geotiff():
    paths = [
        (
            test_data
            / (
                f"geotiff/dry_matter_productivity/dmp_300m_v1_10daily/2024/20240820/"
                f"c_gls_DMP300-{band}-RT1_202408200000_GLOBE_OLCI_V1.1.1.tiff"
            )
        )
        for band in ("DMP", "QFLAG")
    ]
    assert all(p.exists() for p in paths)

    settings = Settings(
        link=LinkSettings(value="c_gls_DMP300-RT1_202408200000_GLOBE_OLCI_V1.1.1"),
    )

    builder = MetadataBuilder(storage=LocalFileSystem(), settings=settings)
    m = builder.build(paths)
    assert m.name == "c_gls_DMP300-RT1_202408200000_GLOBE_OLCI_V1.1.1"
    assert m.name_suffix == "cog"
    assert m.content_type == "application/tiff"
    assert m.get_attribute("datasetIdentifier").value == "dmp_global_300m_10daily_v1"
    assert m.get_attribute("nominalResolutionMeters").value == 300
    assert m.get_attribute("platformShortName").value == "SENTINEL-3"
    assert m.get_attribute("instrumentShortName").value == "OLCI"

@pytest.mark.parametrize(
    ("file_name", "file_namespace"),#, "resolution", "platform_name", "instrument_name"),
    [
        ("c_gls_SCE500_201703010000_CEURO_MODIS_V1.0.1.nc", "netcdf/snow_cover_extent/sce_500m_v1_daily/2017/20170301"),#, 500, "TERRA", "MODIS"),
        ("c_gls_SCE_201801090000_NHEMI_VIIRS_V1.0.1.nc", "netcdf/snow_cover_extent/sce_1km_v1_daily/2018/20180109"),
        ("c_gls_SWE5K_200601010000_NHEMI_SSMIS_V1.0.2.nc", "netcdf/snow_water_equivalent/swe_5km_v1_daily/2006/20060101"),
        ("c_gls_LSWT_201611010000_GLOBE_SLSTRA_v1.0.2.nc", "netcdf/lake_surface_water_temperature/lswt_1km_v1_10daily-nrt/2016/20161101"),#, 1000, "SENTINEL-3", "SLSTRA"),
        ("c_gls_LSWT_200205110000_GLOBE_AATSR_v1.0.2.nc", "netcdf/lake_surface_water_temperature/lswt_1km_v1_10daily-reproc/2002/20020511"),
        ("c_gls_WB100_202010010000_GLOBE_S2_V1.0.1.nc", "netcdf/water_bodies/wb_100m_v1_monthly/2020/20201001"),
        ("c_gls_WB300_202010010000_GLOBE_S2_V2.0.1.nc", "netcdf/water_bodies/wb_300m_v2_monthly/2020/20201001"),
        ("c_gls_LWQ100_201812210000_GLOBAL_MSI_V1.3.nc", "netcdf/lake_water_quality/lwq_100m_v1_10daily-nrt/2018/20181221"),
        ("c_gls_LWQ300_201604210000_GLOBE_OLCI_V1.3.0.nc", "netcdf/lake_water_quality/lwq_300m_v1_10daily-nrt/2016/20160421"),#, 300, None, "OLCI"),
        ("c_gls_LWQ300_200205110000_GLOBE_MERIS_V1.3.0.nc", "netcdf/lake_water_quality/lwq_300m_v1_10daily-reproc/2002/20020511"),
        ("c_gls_LIE250_201703150000_Baltic_MODIS_V1.0.1.nc", "netcdf/lake_ice_extent/lie_250m_v1_daily/2017/20170315"),
        ("c_gls_LIE-NH_202104010000_NHEMI_SLSTR_V1.1.1.nc", "netcdf/lake_ice_extent/lie_500m_v1_daily/2021/20210401"),
    ]
)
def test_cls_netcdf_products(tmp_path, file_name, file_namespace):#, resolution, platform_name, instrument_name):
    current_folder = Path(__file__).parent.resolve()
    data_folder = current_folder / 'data' / 'cls'
    test_data_path = tmp_path / file_namespace / file_name

    test_data_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(data_folder / file_name, test_data_path)

    builder = MetadataBuilder(storage=LocalFileSystem(), settings=Settings())
    m = builder.build((test_data_path,))
    pprint({
        "name": m.name,
        "name_suffix": m.name_suffix,
        "content_type": m.content_type,
        "nominalResolution": m.get_attribute("nominalResolution").value,
        "platformShortName": m.get_attribute("platformShortName").value,
        "instrumentShortName": m.get_attribute("instrumentShortName").value,
        "processingCenter": m.get_attribute("processingCenter").value,
        "product_type": m.product_type,
        "collectionIdentifier": m.get_attribute("collectionIdentifier").value,
        "collectionVersion": m.get_attribute("collectionVersion").value,
        "component": m.get_attribute("component").value,
        "fileFormat": m.get_attribute("fileFormat").value,
        "temporalGrid": m.get_attribute("temporalGrid").value,
    })
