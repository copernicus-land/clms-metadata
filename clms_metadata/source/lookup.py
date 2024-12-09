import re
from pathlib import Path

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
}

PRODUCT = {  # dataset name to collection identifier
    re.compile(r"ndvi[_-]"): "vegetation_indices",
    re.compile(r"g?dmp[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"wl-(rivers|lakes)_"): "river_and_lake_water_level",
}

COMPONENT = {  # components to product types
    "bio-geophysical": {
        "vegetation_indices",
        "dry-gross_dry_matter_productivity",
        "river_and_lake_water_level",
    }
}


class LookupSource(MetadataSource):
    """
    Extract metadata information using lookup tables.
    """

    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        if not metadata.has_attribute(attributes.DATASET_IDENTIFIER):
            for regex, value in DATASET.items():
                if match := regex.match(metadata.name):
                    metadata.add_attribute(
                        name=attributes.DATASET_IDENTIFIER,
                        value_type=StringAttribute,
                        factory=lambda: value.format_map(match.groupdict()),
                    )
                    break
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
            for regex, value in PRODUCT.items():
                if match := regex.match(collection_identifier):
                    metadata.product_type = value
                    break
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
