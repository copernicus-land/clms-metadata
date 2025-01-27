import re
from typing import Final

from clms_metadata.constants.content_type import (
    CONTENT_TYPE_GEOJSON,
    CONTENT_TYPE_NETCDF,
    CONTENT_TYPE_SHP,
    CONTENT_TYPE_TIFF,
    FILE_FORMAT_GEOJSON,
    FILE_FORMAT_NETCDF,
    FILE_FORMAT_SHP,
    FILE_FORMAT_TIFF,
)

CONTENT_TYPE_TO_FILE_FORMAT: dict[str, str] = {
    CONTENT_TYPE_TIFF: FILE_FORMAT_TIFF,
    CONTENT_TYPE_NETCDF: FILE_FORMAT_NETCDF,
    CONTENT_TYPE_GEOJSON: FILE_FORMAT_GEOJSON,
    CONTENT_TYPE_SHP: FILE_FORMAT_SHP,
}

INSTRUMENT_MISSION_MAPPING = {  # Some products have no mission metadata, so we need to derive it from the instrument name
    "OLCI": "SENTINEL3",
    "SLSTR": "SENTINEL3",
    "MSI": "SENTINEL2",
    "SAR": "SENTINEL1",
}

MISSION_TO_INSTRUMENT = {  # mapping of missions with only one instrument
    "PROBAV": "VEGETATION",
    "SPOT4": "VEGETATION",
    "SPOT5": "VEGETATION",
    "SENTINEL1": "SAR",
    "SENTINEL2": "MSI",
    "TERRA": "MODIS",
    "AQUA": "MODIS",
}

IDENTIFIER_TAG_DATASET_IDENTIFIER_MAPPING = {
    # re.compile(r"lie_v(?P<version_major>\d+)_250m"): "lie_baltic_250m_daily_v{version_major}",
    # re.compile(r"lie_v(?P<version_major>\d+)_250m"): "lie_europe_250m_daily_v{version_major}",
    re.compile(
        r"sce500_v(?P<version_major>\d+)_0.005degree"
    ): "sce_europe_500m_daily_v{version_major}",
    re.compile(
        r"lie_nh_v(?P<version_major>\d+)_500m"
    ): "lie_northernhemisphere_500m_daily_v{version_major}",
    # 'lswt_v1_1km': 'lswt-offline_global_1km_10daily_v{version_major}',
    # 'lswt_v1_1km': 'lswt-nrt_global_1km_10daily_v{version_major}',
    re.compile(
        r"lwq_v(?P<version_major>\d+)_100"
    ): "lwq-nrt_global_100m_10daily_v{version_major}",
    # 'lwq_v1_300': 'lwq-reproc_global_300m_10daily_v{version_major}',
    # 'lwq_v1_300': 'lwq-nrt_global_300m_10daily_v{version_major}',
    re.compile(
        r"sce_v(?P<version_major>\d+)_0.01degree"
    ): "sce_northernhemisphere_1km_daily_v{version_major}",
    re.compile(
        r"swe_V(?P<version_major>\d+)_5km"
    ): "swe_northernhemisphere_5km_daily_v{version_major}",
    re.compile(
        r"wb_v(?P<version_major>\d+)_100m"
    ): "wb_global_100m_monthly_v{version_major}",
    re.compile(
        r"wb_v(?P<version_major>\d+)_300m"
    ): "wb_global_300m_monthly_v{version_major}",
    re.compile(
        r"(?P<variable>ndvi|fapar|fcover|lai)_v(?P<version_major>\d+)_1km"
    ): "{variable}_global_1km_10daily_v{version_major}",
    re.compile(
        r"(?P<variable>ndvi|fapar|fcover|lai|dmp|gdmp|npp|gpp)300_v(?P<version_major>\d+)_333m"
    ): "{variable}_global_300m_10daily_v{version_major}",
    re.compile(
        r"lst_v(?P<version_major>\d+)_0.045degree"
    ): "lst_global_5km_hourly_v{version_major}",
    re.compile(
        r"lst10-dc_v(?P<version_major>\d+)_0.045degree"
    ): "lst-daily-cycle_global_5km_10daily_v{version_major}",
    re.compile(
        r"lst10-tci_v(?P<version_major>\d+)_0.045degree"
    ): "lst-tci_global_5km_10daily_v{version_major}",
    re.compile(
        r"swi10_v(?P<version_major>\d+)_0.1degree"
    ): "swi_global_12.5km_10daily_v{version_major}",
    re.compile(
        r"swi_v(?P<version_major>\d+)_0.1degree"
    ): "swi_global_12.5km_daily_v{version_major}",
    re.compile(
        r"swits_v(?P<version_major>\d+)_12.5km"
    ): "swi-timeseries_global_12.5km_daily_v{version_major}",
    re.compile(
        r"swi-static-[a-z]+_v(?P<version_major>\d+)_0.1degree",
    ): "swi-static_global_12.5km_daily_v{version_major}",
    re.compile(
        r"ssm_v(?P<version_major>\d+)_1km"
    ): "ssm_europe_1km_daily_v{version_major}",
}
PRODUCT_NAME_TO_DATASET: Final[
    dict[re.Pattern, str]
] = {  # product name regex to collection identifier
    re.compile(
        r"c_gls_BA300-NRT_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "ba_global_300m_daily_v{version_major}",
    re.compile(
        r"c_gls_BA300-NTC_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "ba_global_300m_monthly_v{version_major}",
    re.compile(
        r"c_gls_(?P<variable>NDVI|FAPAR|FCOVER|LAI)(?:-(RT\d))?_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "{variable}_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_(?P<variable>DMP|GDMP|NPP|GPP|FAPAR|FCOVER|NDVI)300(?:-(RT\d))?_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "{variable}_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_(?P<variable>DMP|GDMP)(?:-(RT\d))?_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "{variable}_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LSWT_\d{12}_GLOBE_AATSR_v(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lswt-offline_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LSWT_\d{12}_GLOBE_SLSTR(?:A|AB)_v(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lswt-nrt_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ300_\d{12}_GLOBE_OLCI_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lwq-nrt_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ300_\d{12}_GLOBE_MERIS_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lwq-reproc_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ100_\d{12}_GLOBAL_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "lwq-nrt_global_100m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LIE-NH_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lie_northernhemisphere_500m_daily_v{version_major}",
    re.compile(
        r"c_gls_LIE250_\d{12}_Baltic_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lie_baltic_250m_daily_v{version_major}",
    re.compile(
        r"c_gls_LIE250_\d{12}_CEURO_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "lie_europe_250m_daily_v{version_major}",
    re.compile(
        r"c_gls_SCE500_\d{12}_CEURO_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "sce_europe_500m_daily_v{version_major}",
    re.compile(
        r"c_gls_SCE_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "sce_northernhemisphere_1km_daily_v{version_major}",
    re.compile(
        r"c_gls_SWE5K_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "swe_northernhemisphere_5km_daily_v{version_major}",
    re.compile(
        r"c_gls_WB100_\d{12}_GLOBE_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "wb_global_100m_monthly_v{version_major}",
    re.compile(
        r"c_gls_WB300_\d{12}_GLOBE_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "wb_global_300m_monthly_v{version_major}",
    re.compile(
        r"c_gls_LWQ1km_\d{12}_GLOBE_OLCI_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "lwq-nrt_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ1km_\d{12}_GLOBE_MERIS_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "lwq-reproc_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LST_\d{12}_GLOBE_GEO_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "lst_global_5km_hourly_v{version_major}",
    re.compile(
        r"c_gls_LST10-DC_\d{12}_GLOBE_GEO_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "lst-daily-cycle_global_5km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LST10-TCI_\d{12}_GLOBE_GEO_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "lst-tci_global_5km_10daily_v{version_major}",
    re.compile(
        r"c_gls_NDVI-(?P<term>STS|LTS)_\d{4}-\d{4}-\d{4}_GLOBE_[-A-Z]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "ndvi-{term}_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_SWI1km_\d{12}_CEURO_[A-Z]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "swi_europe_1km_daily_v{version_major}",
    re.compile(
        r"c_gls_SWI-TS_\d{12}_\w+_[A-Z]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "swi-timeseries_global_12.5km_daily_v{version_major}",
    re.compile(
        r"c_gls_SWI-STATIC-[A-Z]+_[\d-]{12}_GLOBE_[A-Z-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "swi-static_global_12.5km_daily_v{version_major}",
    re.compile(
        r"c_gls_SSM1km_\d{12}_CEURO_[A-Z-]+_V(?P<version>(?P<version_major>\d)\.\d\.\d)"
    ): "ssm_europe_1km_daily_v{version_major}",
}
DATASET_TO_PRODUCT_TYPE = {  # dataset name to product type
    re.compile(r"ndvi[_-]"): "vegetation_indices",
    re.compile(r"dmp|gdmp|gpp|npp[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"wl-(rivers|lakes)_"): "river_and_lake_water_level",
    re.compile(r"(fapar|fcover|lai)[_-]"): "vegetation_properties",
    re.compile(r"^sce"): "snow_cover_extent",
    re.compile(r"^swe"): "snow_water_equivalent",
    re.compile(r"(lswt|lst)[_-]"): "land_surface_temperature",
    re.compile(r"^wb"): "water_bodies",
    re.compile(r"^lwq"): "lake_water_quality",
    re.compile(r"^lie"): "river_and_lake_ice_extent",
    re.compile(r"ba_"): "burnt_area",
    re.compile(r"swi[_-]"): "soil_water_index",
    re.compile(r"ssm_"): "surface_soil_moisture",
}
COMPONENT_TO_PRODUCT_TYPES = {  # components to product types
    "bio-geophysical": {
        "vegetation_indices",
        "dry-gross_dry_matter_productivity",
        "snow_cover_extent",
        "snow_water_equivalent",
        "land_surface_temperature",
        "water_bodies",
        "lake_water_quality",
        "river_and_lake_ice_extent",
        "vegetation_properties",
        "river_and_lake_water_level",
        "burnt_area",
        "soil_water_index",
        "surface_soil_moisture",
    }
}
DATASET_SHORT_NAMES = {
    "lc",
    "ssm",
    "swi",
    "swi-ts",
    "swi-sl",
    "swi",
    "swe",
    "sce",
    "lst",
    "lst-dc",
    "lst-tci",
    "lswt",
    "tcr",
    "ba",
    "fgvc",
    "fapar",
    "lai",
    "ndvi",
    "ndvi-sts",
    "ndvi-lts",
    "lsp",
    "dmp",
    "gdmp",
    "npp",
    "gpp",
    "wb",
    "lwl",
    "rwl",
    "lwq",
    "lie",
}
DATASET_NAME_TO_SHORT_NAME = {
    re.compile(r"wl-rivers"): "rwl",
    re.compile(r"wl-lakes"): "lwl",
    re.compile(r"lwq"): "lwq",
    re.compile(r"lswt"): "lswt",
    re.compile(r"fcover"): "fgvc",
    re.compile(r"lst-daily-cycle"): "lst-dc",
    re.compile(r"swi-timeseries"): "swi-ts",
    re.compile(r"swi-static"): "swi-sl",
}

SPATIAL_EXTENT_MAPPING = {"northernhemisphere": "northern hemisphere"}

MISSION_TO_PLATFORM = {
    re.compile(
        r"(?P<name>(PROBAV)|(SPOT\d+)|(TERRA)|(AQUA)|(METEOSAT\d+)|(HIMAWARI[89])|(ENVISAT)|(NOAA20))"
    ): "{name}",  # literal
    re.compile(r"HIMAWARI6"): "MTSAT1R",
    re.compile(r"HIMAWARI7"): "MTSAT2",
    re.compile(r"SUOMI NPP"): "NPP",
}

PLATFORM_SHORT_NAME_TO_ACRONYM = {
    re.compile(
        r"SENTINEL(?P<num>\d+)(?P<serial>[A-Z]+)"
    ): "S{num}{serial}",  # Sentinel platforms
    re.compile(r"(?P<name>(PROBAV)|(SPOT\d))"): "{name}",  # literal
    re.compile(r"TERRA"): "EOS AM-1",
    re.compile(r"ACQUA"): "EOS PM-1",
}
