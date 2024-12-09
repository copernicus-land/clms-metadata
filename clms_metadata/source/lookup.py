import re
from pathlib import Path
from typing import Optional

from cloudpathlib import CloudPath

from clms_metadata.constants import attributes
from clms_metadata.models import IntegerAttribute, Metadata, StringAttribute
from clms_metadata.source import MetadataSource

REGEX_RESOLUTION = re.compile(r"_([\d.]+)(m|km)_")
REGEX_NUM_TEMPORAL = re.compile(r"(\d+)([a-z]+)")
DATASET = {  # product name regex to collection identifier
    re.compile(
        r"c_gls_NDVI_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "ndvi_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_DMP300-RT\d_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "dmp_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LSWT_\d{12}_GLOBE_AATSR_v(?P<version>(?P<version_major>\d).\d.\d)"):
        "lswt-offline_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LSWT_\d{12}_GLOBE_SLSTR(?:A|AB)_v(?P<version>(?P<version_major>\d).\d.\d)"):
        "lswt-nrt_global_1km_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ300_\d{12}_GLOBE_OLCI_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "lwq-nrt_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ300_\d{12}_GLOBE_MERIS_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "lwq-reproc_global_300m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LWQ100_\d{12}_GLOBAL_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d)"):
        "lwq-nrt_global_100m_10daily_v{version_major}",
    re.compile(
        r"c_gls_LIE-NH_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "lie_northernhemisphere_500m_daily_v{version_major}",
    re.compile(
        r"c_gls_LIE250_\d{12}_Baltic_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "lie_baltic_250m_daily_v{version_major}",
    re.compile(
        r"c_gls_SCE500_\d{12}_CEURO_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "sce_europe_500m_daily_v{version_major}",
    re.compile(
        r"c_gls_SCE_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "sce_northernhemisphere_1km_daily_v{version_major}",
    re.compile(
        r"c_gls_SWE5K_\d{12}_NHEMI_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "swe_northernhemisphere_5km_daily_v{version_major}",
    re.compile(
        r"c_gls_WB100_\d{12}_GLOBE_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "wb_global_100m_monthly_v{version_major}",
    re.compile(
        r"c_gls_WB300_\d{12}_GLOBE_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"):
        "wb_global_300m_monthly_v{version_major}"
}

PRODUCT = {  # dataset name to collection identifier
    re.compile(r"ndvi[_-]"): "vegetation_indices",
    re.compile(r"g?dmp[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"^sce"): "snow_cover_extent",
    re.compile(r"^swe"): "snow_water_equivalent",
    re.compile(r"^lswt"): "land_surface_temperature",
    re.compile(r"^wb"): "water_bodies",
    re.compile(r"^lwq"): "lake_water_quality",
    re.compile(r"^lie"): "river_and_lake_ice_extent",
}

COMPONENT = {  # components to product types
    "bio-geophysical": {"vegetation_indices", "dry-gross_dry_matter_productivity","snow_cover_extent",
                        "snow_water_equivalent", "land_surface_temperature", "water_bodies",
                        "lake_water_quality", "river_and_lake_ice_extent",}
}


class LookupSource(MetadataSource):
    """
    Extract metadata information using lookup tables.
    """

    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        if not metadata.has_attribute(attributes.DATASET_IDENTIFIER):
            if collection_identifier := self.extract_collection_id(file_name=metadata.name):
                metadata.add_attribute(
                    name=attributes.DATASET_IDENTIFIER,
                    value_type=StringAttribute,
                    factory=lambda: collection_identifier,
                )
        collection_identifier = metadata.get_attribute(
            attributes.DATASET_IDENTIFIER
        ).value
        metadata.add_attribute(
            name=attributes.DATASET_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: collection_identifier.split("_")[0],
        )  # TODO: check if correct
        metadata.add_attribute(
            name=attributes.DATASET_ALIAS,
            value_type=StringAttribute,
            factory=lambda: collection_identifier[: collection_identifier.rfind("_")],
        )

        if not metadata.product_type:
            metadata.product_type = self.determine_product_type(collection_identifier)
        if not metadata.has_attribute(attributes.COMPONENT):
            for component, product_types in COMPONENT.items():
                if metadata.product_type in product_types:
                    metadata.add_attribute(
                        attributes.COMPONENT, StringAttribute, lambda: component
                    )

        metadata.add_attribute(
            name=attributes.SPATIAL_EXTENT,
            value_type=StringAttribute,
            factory=lambda: get_spatial_extent(collection_identifier),
        )

        metadata.add_attribute(
            attributes.NOMINAL_RESOLUTION_METERS,
            IntegerAttribute,
            lambda: get_resolution(collection_identifier),
        )
        metadata.add_attribute(
            name=attributes.NOMINAL_RESOLUTION,
            value_type=StringAttribute,
            factory=lambda: collection_identifier.split("_")[2],
        )
        metadata.add_attribute(
            name=attributes.TEMPORAL_GRID,
            value_type=StringAttribute,
            factory=lambda: get_temporal_grid(collection_identifier),
        )

        return metadata

    @staticmethod
    def extract_collection_id(file_name: str) -> Optional[str]:
        """
        Iterate through regexes for all known collections until a match with the filename is found.
        Extract the major version number from the filename and use it to complete the collection identifier.

        :param file_name: The name of the file currently being processed
        :return: The collection identifier of the collection to which the file belongs.
        :raises ValueError: No match was found
        """
        for regex, value in DATASET.items():
            if match := regex.match(file_name):
                return value.format_map(match.groupdict())
        raise ValueError(f'No collection regex match was found for filename {file_name}')

    @staticmethod
    def determine_product_type(collection_id: str) -> Optional[str]:
        """
        Look for a match on the product identifier to map to the corresponding product type
        :param collection_id: The identifier of the collection
        :return: The product type of the collection if a match is found, None otherwise
        """
        for regex, product_type in PRODUCT.items():
            if regex.match(collection_id):
                return product_type


def get_resolution(collection_identifier: str) -> int | None:
    """
    Derive the resolution from the collection identifier.

    :param collection_identifier: collection identifier
    :return: nominal resolution
    """
    if match := REGEX_RESOLUTION.search(collection_identifier):
        factor = 1000 if match.group(2) == "km" else 1
        res_base = float(match.group(1))
        resolution = int(res_base * factor)
        return resolution
    else:
        return None


def get_spatial_extent(collection_identifier: str) -> str:
    """
    Derive the spatial extent from the collection identifier.

    :param collection_identifier: collection identifier
    :return: spatial extent as a string
    """
    return collection_identifier.split("_")[1]


def get_temporal_grid(collection_identifier: str) -> str:
    """
    Derive the temporal grid from the dataset name.

    :param collection_identifier: dataset name
    :return:
    """
    temp = collection_identifier.split("_")[3]
    # add separator between numbers and unit
    if match := REGEX_NUM_TEMPORAL.match(temp):
        return f"{match.group(1)}-{match.group(2)}"
    return temp
