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

IDENTIFIER_TAG_DATASET_IDENTIFIER_MAPPING: Final[dict[re.Pattern, str]] = {
    re.compile(
        r"eta_300_10daily_v(?P<version_major>\d+)_300m"
    ): "eta_global_300m_10daily_v{version_major}",
    re.compile(
        r"hf_daily_v(?P<version_major>\d+)_300m"
    ): "hf_global_300m_daily_v{version_major}",
}

PRODUCT_NAME_TO_DATASET: Final[
    dict[re.Pattern, str]
] = {  # product name regex to collection identifier
    re.compile(
        r"LCFM_LCM-(?P<resolution>\d+)_V(?P<version>(?P<version_major>\d)\d\d)_(?P<year>\d{4})_(?P<tile>\w+)"
    ): "lcm_global_{resolution}m_yearly_v{version_major}",
    re.compile(
        r"LCFM_TCD-(?P<resolution>\d+)_V(?P<version>(?P<version_major>\d)\d\d)_(?P<year>\d{4})_(?P<tile>\w+)"
    ): "tcd_pantropical_{resolution}m_yearly_v{version_major}",
    re.compile(
        r"LCFM_LSC-(?P<resolution>\d+)-ANNUAL_V(?P<version>(?P<version_major>\d)\d\d)_(?P<year>\d{4})_(?P<tile>\w+)"
    ): "lsc_global_{resolution}m_yearly_v{version_major}",
    re.compile(
        r"LCFM_LSC-(?P<resolution>\d+)-MONTHLY_V(?P<version>(?P<version_major>\d)\d\d)_(?P<year>\d{4})_(?P<tile>\w+)"
    ): "lsc_global_{resolution}m_monthly_v{version_major}",
    re.compile(
        r"clms_HF300_\d{12}_GLOBE_S3_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "hf_global_300m_daily_v{version_major}",
    re.compile(
        r"clms_ETA300_\d{12}_GLOBE_S3_V(?P<version>(?P<version_major>\d)\.\d)"
    ): "eta_global_300m_10daily_v{version_major}",
}

DATASET_TO_PRODUCT_TYPE = {  # dataset name to product type
    re.compile(r"^ndvi[_-]"): "vegetation_indices",
    re.compile(r"^(dmp|gdmp)[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"^(gpp|npp)[_-]"): "net-gross_primary_production",
    re.compile(r"^wl-(rivers|lakes)_"): "river_and_lake_water_level",
    re.compile(r"^(fapar|fcover|lai)[_-]"): "vegetation_properties",
    re.compile(r"^sce"): "snow_cover_extent",
    re.compile(r"^swe"): "snow_water_equivalent",
    re.compile(r"^lst[_-]"): "land_surface_temperature",
    re.compile(r"^lswt[_-]"): "lake_surface_water_temperature",
    re.compile(r"^wb"): "water_bodies",
    re.compile(r"^lwq"): "lake_water_quality",
    re.compile(r"^lie"): "river_and_lake_ice_extent",
    re.compile(r"^ba_"): "burnt_area",
    re.compile(r"^swi[_-]"): "soil_water_index",
    re.compile(r"^ssm_"): "surface_soil_moisture",
    re.compile(r"^(lc_global|lcm|tcd|lsc)_"): "dynamic_land_cover",
    re.compile(r"^toc_"): "top-of-canopy_reflectances",
    re.compile(r"^lsp_"): "vegetation_phenology_and_productivity_parameters",
    re.compile(r"^hf_"): "evapotranspiration",
    re.compile(r"^eta_"): "evapotranspiration",
}
COMPONENT_TO_PRODUCT_TYPES = {  # components to product types
    "bio-geophysical": {
        "vegetation_indices",
        "dry-gross_dry_matter_productivity",
        "net-gross_primary_production",
        "snow_cover_extent",
        "snow_water_equivalent",
        "land_surface_temperature",
        "lake_surface_water_temperature",
        "water_bodies",
        "lake_water_quality",
        "river_and_lake_ice_extent",
        "vegetation_properties",
        "river_and_lake_water_level",
        "burnt_area",
        "soil_water_index",
        "surface_soil_moisture",
        "top-of-canopy_reflectances",
        "vegetation_phenology_and_productivity_parameters",
        "evapotranspiration",
    },
    "landcover_landuse": {"dynamic_land_cover", "crop_types", "cropping_patterns"},
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
    "lsc",
    "lcm",
    "tcd",
    "eta",
    "hf",
}
DATASET_NAME_TO_SHORT_NAME = {
    re.compile(r"^wl-rivers"): "rwl",
    re.compile(r"^wl-lakes"): "lwl",
    re.compile(r"^lwq"): "lwq",
    re.compile(r"^lswt"): "lswt",
}

SPATIAL_EXTENT_MAPPING = {
    "northernhemisphere": "northern hemisphere",
    "pantropical": "pan tropical",
}

COG_EXTENSIONS = [".tiff", ".tif", ".geotiff", ".geotif", ".cog"]
