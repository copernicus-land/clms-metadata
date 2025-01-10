import re

INSTRUMENT_MISSION_MAPPING = {  # Some products have no mission metadata, so we need to derive it from the instrument name
    "OLCI": "SENTINEL-3",
    "SLSTR": "SENTINEL-3",
    "MSI": "SENTINEL-2",
}

IDENTIFIER_TAG_DATASET_IDENTIFIER_MAPPING = {
    "lie_v1_250m": "lie_baltic_250m_daily_v{version_major}",
    "sce500_v1_0.005degree": "sce_europe_500m_daily_v{version_major}",
    "lie_nh_v1_500m": "lie_northernhemisphere_500m_daily_v{version_major}",
    # 'lswt_v1_1km': 'lswt-offline_global_1km_10daily_v{version_major}',
    # 'lswt_v1_1km': 'lswt-nrt_global_1km_10daily_v{version_major}',
    "lwq_v1_100": "lwq-nrt_global_100m_10daily_v{version_major}",
    # 'lwq_v1_300': 'lwq-reproc_global_300m_10daily_v{version_major}',
    # 'lwq_v1_300': 'lwq-nrt_global_300m_10daily_v{version_major}',
    "sce_v1_0.01degree": "sce_northernhemisphere_1km_daily_v{version_major}",
    "swe_V1_5km": "swe_northernhemisphere_5km_daily_v{version_major}",
    "wb_v1_100m": "wb_global_100m_monthly_v{version_major}",
    "wb_v2_300m": "wb_global_300m_monthly_v{version_major}",
    "ndvi_v3_1km": "ndvi_global_1km_10daily_v{version_major}",
    "fapar300_v1_333m": "fapar_global_300m_10daily_v{version_major}",
}
PRODUCT_NAME_TO_DATASET = {  # product name regex to collection identifier
    re.compile(
        r"c_gls_NDVI_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "ndvi_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_DMP300-RT\d_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "dmp_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_FAPAR300-RT\d_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "fapar_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LSWT_\d{12}_GLOBE_AATSR_v(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lswt-offline_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LSWT_\d{12}_GLOBE_SLSTR(?:A|AB)_v(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lswt-nrt_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ300_\d{12}_GLOBE_OLCI_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lwq-nrt_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ300_\d{12}_GLOBE_MERIS_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lwq-reproc_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ100_\d{12}_GLOBAL_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d)"
    ): "lwq-nrt_global_100m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LIE-NH_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lie_northernhemisphere_500m_daily_v{version_major}",
    re.compile(
        r"c_gls_LIE250_\d{12}_Baltic_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lie_baltic_250m_daily_v{version_major}",
    re.compile(
        r"c_gls_LIE250_\d{12}_CEURO_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "lie_europe_250m_daily_v{version_major}",
    re.compile(
        r"c_gls_SCE500_\d{12}_CEURO_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "sce_europe_500m_daily_v{version_major}",
    re.compile(
        r"c_gls_SCE_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "sce_northernhemisphere_1km_daily_v{version_major}",
    re.compile(
        r"c_gls_SWE5K_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "swe_northernhemisphere_5km_daily_v{version_major}",
    re.compile(
        r"c_gls_WB100_\d{12}_GLOBE_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "wb_global_100m_monthly_v{version_major}",
    re.compile(
        r"c_gls_WB300_\d{12}_GLOBE_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "wb_global_300m_monthly_v{version_major}",
    re.compile(
        r"c_gls_LWQ1km_\d{12}_GLOBE_OLCI_V(?P<version>(?P<version_major>\d).\d)"
    ): "lwq-nrt_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ1km_\d{12}_GLOBE_MERIS_V(?P<version>(?P<version_major>\d).\d)"
    ): "lwq-reproc_global_1km_10daily_v{version_major}",
}
DATASET_TO_PRODUCT_TYPE = {  # dataset name to product type
    re.compile(r"ndvi[_-]"): "vegetation_indices",
    re.compile(r"g?dmp[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"wl-(rivers|lakes)_"): "river_and_lake_water_level",
    re.compile(r"(fapar|fcover|lai)[_-]"): "vegetation_properties",
    re.compile(r"^sce"): "snow_cover_extent",
    re.compile(r"^swe"): "snow_water_equivalent",
    re.compile(r"^lswt"): "land_surface_temperature",
    re.compile(r"^wb"): "water_bodies",
    re.compile(r"^lwq"): "lake_water_quality",
    re.compile(r"^lie"): "river_and_lake_ice_extent",
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
}

SPATIAL_EXTENT_MAPPING = {"northernhemisphere": "northern hemisphere"}

MISSION_TO_PLATFORM = {
    re.compile(
        r"(?P<name>(PROBAV)|(SPOT\d+)|(TERRA)|(AQUA)|(METEOSAT\d+)|(HIMAWARI[89])|(ENVISAT))"
    ): "{name}",  # literal
    re.compile(r"HIMAWARI6"): "MTSAT1R",
    re.compile(r"HIMAWARI7"): "MTSAT2",
}

PLATFORM_SHORT_NAME_TO_ACRONYM = {
    re.compile(
        r"SENTINEL(?P<num>\d+)(?P<serial>[A-Z]+)"
    ): "S{num}{serial}",  # Sentinel platforms
    re.compile(r"(?P<name>(PROBAV)|(SPOT\d))"): "{name}",  # literal
}
