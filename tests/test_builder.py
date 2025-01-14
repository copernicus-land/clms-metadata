from pathlib import Path

import pyjson5
import pytest

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import LinkSettings, Settings
from clms_metadata.models import ContentDate, Metadata
from clms_metadata.storage import LocalFileSystem

test_root = Path(__file__).parent
test_data = test_root / "data"
test_reference = test_root / "reference"


@pytest.mark.parametrize(
    ("files", "reference"),
    [
        # ndvi_global_1km_10daily_v3
        (
            (
                test_data
                / "ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1.nc",
            ),
            test_reference
            / "ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1_nc.json5",
        ),
        (
            tuple(
                test_data
                / "ndvi_global_1km_10daily_v3"
                / f"c_gls_NDVI-{band}_199901010000_GLOBE_VGT_V3.0.1.tiff"
                for band in ("NDVI", "NOBS", "QFLAG", "TIMEGRID", "UNC")
            ),
            test_reference
            / "ndvi_global_1km_10daily_v3/c_gls_NDVI_199901010000_GLOBE_VGT_V3.0.1_cog.json5",
        ),
        # ba_global_300m_daily_v3
        (
            (
                test_data
                / "ba_global_300m_daily_v3/c_gls_BA300-NRT_202402200000_GLOBE_S3_V3.1.1.nc",
            ),
            test_reference
            / "ba_global_300m_daily_v3/c_gls_BA300-NRT_202402200000_GLOBE_S3_V3.1.1_nc.json5",
        ),
        # ba_global_300m_daily_v3
        (
            (
                test_data
                / "ba_global_300m_monthly_v3/c_gls_BA300-NTC_202306010000_GLOBE_S3_V3.1.1.nc",
            ),
            test_reference
            / "ba_global_300m_monthly_v3/c_gls_BA300-NTC_202306010000_GLOBE_S3_V3.1.1_nc.json5",
        ),
    ],
)
def test_builder(files, reference):
    assert all(p.exists() for p in files)

    builder = MetadataBuilder(
        storage=LocalFileSystem(), settings=Settings(link=LinkSettings(value="test"))
    )
    m = builder.build(files)
    print(m)
    compare_with_reference_file(m, reference)


@pytest.mark.parametrize(
    ("name", "files", "content_date"),
    [
        (
            "c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2",
            (
                test_root
                / "data/fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2.nc",
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
    assert m.get_attribute("metricGridSpacing").value == 300
    assert m.get_attribute("platformShortName").value == "SENTINEL-3"
    assert m.get_attribute("instrumentShortName").value == "OLCI"


@pytest.mark.parametrize(
    "file_name",
    [
        "c_gls_SCE500_201703010000_CEURO_MODIS_V1.0.1.nc",
        "c_gls_SCE_201801090000_NHEMI_VIIRS_V1.0.1.nc",
        "c_gls_SWE5K_200601010000_NHEMI_SSMIS_V1.0.2.nc",
        "c_gls_LSWT_201611010000_GLOBE_SLSTRA_v1.0.2.nc",
        "c_gls_LSWT_200205110000_GLOBE_AATSR_v1.0.2.nc",
        "c_gls_WB100_202010010000_GLOBE_S2_V1.0.1.nc",
        "c_gls_WB300_202010010000_GLOBE_S2_V2.0.1.nc",
        "c_gls_LWQ100_201812210000_GLOBAL_MSI_V1.3.nc",
        "c_gls_LWQ300_201604210000_GLOBE_OLCI_V1.3.0.nc",
        "c_gls_LWQ300_200205110000_GLOBE_MERIS_V1.3.0.nc",
        "c_gls_LIE250_201703150000_Baltic_MODIS_V1.0.1.nc",
        "c_gls_LIE-NH_202104010000_NHEMI_SLSTR_V1.1.1.nc",
        "c_gls_LWQ1km_201604210000_GLOBE_OLCI_V1.2.nc",  # clms_global_lwq_1km_v1_10daily-nrt_netcdf
        "c_gls_SWE5K_202407010000_NHEMI_SSMIS_V2.0.1.nc",  # clms_global_swe_5km_v2_daily_netcdf
        "c_gls_LWQ300_202409010000_GLOBE_OLCI_V2.0.0.nc",  # clms_global_lwq_300m_v2_10daily-nrt_netcdf
        "c_gls_LWQ1km_200205110000_GLOBE_MERIS_V1.1.nc",  # clms_global_lwq_1km_v1_10daily-reproc_netcdf
        "c_gls_LWQ100_202409010000_GLOBAL_MSI_V2.0.nc",  # clms_global_lwq_100m_v2_10daily-nrt_netcdf
        "c_gls_LIE250_202402190000_CEURO_VIIRS_V2.2.1.nc",
    ],
)
def test_cls_netcdf_products(file_name):
    with open(
        test_root / "reference" / "cls" / "cls_datasets_expected_metadata.json5", "r"
    ) as f:
        expected_data = [
            d for d in pyjson5.load(f) if d.get("name") == file_name.replace(".nc", "")
        ][0]

    builder = MetadataBuilder(storage=LocalFileSystem(), settings=Settings())
    m = builder.build((test_data / "cls" / file_name,))

    compare_with_reference(m, expected_data)


@pytest.mark.parametrize(
    ("path", "reference"),
    [
        (
            test_root
            / "data/wl-lakes_global_vector_daily_v2/c_gls_WL_202412050703_1300000000166_ALTI_V2.2.0.json",
            test_root
            / "reference/wl-lakes_global_vector_daily_v2/c_gls_WL_202412050703_1300000000166_ALTI_V2.2.0.json",
        ),
        (
            test_root
            / "data/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json",
            test_root
            / "reference/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json5",
        ),
    ],
)
def test_water_level_global_vector_daily(path, reference):
    assert path.exists()
    builder = MetadataBuilder(storage=LocalFileSystem(), settings=Settings())
    m = builder.build((path,))

    compare_with_reference_file(m, reference)


def compare_with_reference_file(m: Metadata, reference: Path):
    """
    Compare the metadata model with a reference

    :param m: metadata model
    :param reference: path to reference file
    :return:
    """
    with open(reference) as f:
        expected = pyjson5.load(f)
    compare_with_reference(m, expected)


def compare_with_reference(m: Metadata, expected: dict):
    """
    Compare the metadata with a reference dictionary.

    :param m: metadata model
    :param expected: reference dictionary
    :return:
    """
    m_dict = m.model_dump()
    expected_attributes = expected.pop("attributes")

    for k, v in expected.items():
        assert v == m_dict.get(k)

    attributes = {a["name"]: a["value"] for a in m_dict["attributes"]}
    assert expected_attributes == {
        k: v for k, v in attributes.items() if k in expected_attributes
    }
