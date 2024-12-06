from pathlib import Path

import pytest

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import LinkSettings, Settings
from clms_metadata.models import ContentDate
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


@pytest.mark.parametrize(
    ("name", "files", "content_date"),
    [
        (
            "c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2",
            (
                test_data
                / "fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2.nc",
            ),
            ContentDate(start="2023-02-01T00:00:00Z", end="2023-02-10T23:59:59.999Z"),
        )
    ],
)
def test_fapar_global_300m_10daily_v1(name, files, content_date):
    assert all(p.exists() for p in files)

    builder = MetadataBuilder(
        storage=LocalFileSystem(), settings=Settings(link=LinkSettings(value="test"))
    )
    m = builder.build(files)
    assert m.name == name
    assert m.content_date == content_date


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
