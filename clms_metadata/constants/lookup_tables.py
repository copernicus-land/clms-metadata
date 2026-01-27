import re

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
}

SPATIAL_EXTENT_MAPPING = {
    "northernhemisphere": "northern hemisphere",
    "pantropical": "pan tropical",
}

COG_EXTENSIONS = [".tiff", ".tif", ".geotiff", ".geotif", ".cog"]
