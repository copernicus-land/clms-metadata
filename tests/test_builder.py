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
                / "vegetation_indices/ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1_nc.json5",
        ),
        (
            tuple(
                test_data
                / "vegetation_indices/ndvi_global_1km_10daily_v3"
                / f"c_gls_NDVI-{band}_199901010000_GLOBE_VGT_V3.0.1.tiff"
                for band in ("NDVI", "NOBS", "QFLAG", "TIMEGRID", "UNC")
            ),
            test_reference
            / "vegetation_indices/ndvi_global_1km_10daily_v3/c_gls_NDVI_199901010000_GLOBE_VGT_V3.0.1_cog.json5",
        ),
        # ba_global_300m_daily_v3
        (
            (
                test_data
                / "burnt_area/ba_global_300m_daily_v3/c_gls_BA300-NRT_202402200000_GLOBE_S3_V3.1.1.nc",
            ),
            test_reference
            / "burnt_area/ba_global_300m_daily_v3/c_gls_BA300-NRT_202402200000_GLOBE_S3_V3.1.1_nc.json5",
        ),
        # ba_global_300m_daily_v3
        (
            (
                test_data
                / "burnt_area/ba_global_300m_monthly_v3/c_gls_BA300-NTC_202306010000_GLOBE_S3_V3.1.1.nc",
            ),
            test_reference
            / "burnt_area/ba_global_300m_monthly_v3/c_gls_BA300-NTC_202306010000_GLOBE_S3_V3.1.1_nc.json5",
        ),
        # dmp_global_1km_10daily_v2/
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/dmp_global_1km_10daily_v2/c_gls_DMP_200109100000_GLOBE_VGT_V2.0.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/dmp_global_1km_10daily_v2/c_gls_DMP_200109100000_GLOBE_VGT_V2.0.1_nc.json5",
        ),
        # dmp_global_300m_10daily_v1
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/dmp_global_300m_10daily_v1/c_gls_DMP300-RT5_201502200000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/dmp_global_300m_10daily_v1/c_gls_DMP300-RT5_201502200000_GLOBE_PROBAV_V1.0.1_nc.json5",
        ),
        # gdmp_global_1km_10daily_v2
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/gdmp_global_1km_10daily_v2/c_gls_GDMP_199901310000_GLOBE_VGT_V2.0.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/gdmp_global_1km_10daily_v2/c_gls_GDMP_199901310000_GLOBE_VGT_V2.0.1_nc.json5",
        ),
        # gdmp_global_300m_10daily_v1
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/gdmp_global_300m_10daily_v1/c_gls_GDMP300-RT0_202501100000_GLOBE_OLCI_V1.1.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/gdmp_global_300m_10daily_v1/c_gls_GDMP300-RT0_202501100000_GLOBE_OLCI_V1.1.1_nc.json5",
        ),
        # gpp_global_300m_10daily_v1
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/gpp_global_300m_10daily_v1/c_gls_GPP300-RT2_202410310000_GLOBE_OLCI_V1.1.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/gpp_global_300m_10daily_v1/c_gls_GPP300-RT2_202410310000_GLOBE_OLCI_V1.1.1_nc.json5",
        ),
        # npp_global_300m_10daily_v1
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/npp_global_300m_10daily_v1/c_gls_NPP300-RT6_202307100000_GLOBE_OLCI_V1.1.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/npp_global_300m_10daily_v1/c_gls_NPP300-RT6_202307100000_GLOBE_OLCI_V1.1.1_nc.json5",
        ),
        # fapar_global_1km_10daily_v2
        (
            (
                test_data
                / "vegetation_properties/fapar_global_1km_10daily_v2/c_gls_FAPAR_199908100000_GLOBE_VGT_V2.0.2.nc",
            ),
            test_reference
            / "vegetation_properties/fapar_global_1km_10daily_v2/c_gls_FAPAR_199908100000_GLOBE_VGT_V2.0.2_nc.json5",
        ),
        # fapar_global_300m_10daily_v1
        (
            (
                test_data
                / "vegetation_properties/fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2.nc",
            ),
            test_reference
            / "vegetation_properties/fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2_nc.json5",
        ),
        # fcover_global_300m_10daily_v1
        (
            (
                test_data
                / "vegetation_properties/fcover_global_300m_10daily_v1/c_gls_FCOVER300_201503200000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "vegetation_properties/fcover_global_300m_10daily_v1/c_gls_FCOVER300_201503200000_GLOBE_PROBAV_V1.0.1_nc.json5",
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
                test_data
                / "vegetation_properties/fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2.nc",
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
            test_data
            / "river_and_lake_water_level/wl-lakes_global_vector_daily_v2/c_gls_WL_202412050703_1300000000166_ALTI_V2.2.0.json",
            test_reference
            / "river_and_lake_water_level/wl-lakes_global_vector_daily_v2/c_gls_WL_202412050703_1300000000166_ALTI_V2.2.0.json",
        ),
        (
            test_data
            / "river_and_lake_water_level/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json",
            test_reference
            / "river_and_lake_water_level/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json5",
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
    try:
        with open(reference) as f:
            expected = pyjson5.load(f)
    except FileNotFoundError as e:
        dump = m.model_dump()
        dump["attributes"] = {a["name"]: a["value"] for a in dump["attributes"]}
        print(dump)
        raise e
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
