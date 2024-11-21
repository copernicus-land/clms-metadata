from pathlib import Path

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import LinkSettings, MetadataSettings, Settings
from clms_metadata.storage import LocalFileSystem

file_root = Path("/data/MTDA/Copernicus/Land/global/")


def test_ndvi_1km_v3_10daily_netcdf():
    path = (
        file_root
        / "netcdf/ndvi/ndvi_1km_v3_10daily/2020/20200401/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1.nc"
    )
    assert path.exists()

    settings = Settings(
        metadata=MetadataSettings(
            dataset_name="ndvi_1km_v3_10daily", product_type="ndvi"
        )
    )

    builder = MetadataBuilder(storage=LocalFileSystem(), settings=settings)
    m = builder.build((path,))
    assert m.name == path.stem
    assert m.name_suffix == "nc"
    assert m.content_type == "application/netcdf"
    assert next(a for a in m.attributes if a.name == "resolution").value == 1000


def test_dmp_300m_v1_10daily_geotiff():
    paths = [
        (
            file_root
            / (
                f"geotiff/dry_matter_productivity/dmp_300m_v1_10daily/2024/20240820/"
                f"c_gls_DMP300-{band}-RT1_202408200000_GLOBE_OLCI_V1.1.1.tiff"
            )
        )
        for band in ("DMP", "QFLAG")
    ]
    assert all(p.exists() for p in paths)

    settings = Settings(
        metadata=MetadataSettings(
            dataset_name="dmp_300m_v1_10daily", product_type="dry_matter_productivity"
        ),
        link=LinkSettings(value="c_gls_DMP300-RT1_202408200000_GLOBE_OLCI_V1.1.1"),
    )

    builder = MetadataBuilder(storage=LocalFileSystem(), settings=settings)
    m = builder.build(paths)
    assert m.name == "c_gls_DMP300-RT1_202408200000_GLOBE_OLCI_V1.1.1"
    assert m.name_suffix == "tiff"
    assert m.content_type == "application/tiff"
    assert next(a for a in m.attributes if a.name == "resolution").value == 300
