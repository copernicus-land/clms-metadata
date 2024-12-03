import re
from pathlib import Path

from cloudpathlib import CloudPath

from clms_metadata.models import IntegerAttribute, Metadata, StringAttribute
from clms_metadata.source import MetadataSource

REGEX_RESOLUTION = re.compile(r"_([\d.]+)(m|km)_")
REGEX_NUM_TEMPORAL = re.compile(r"(\d+)([a-z]+)")
DATASET = {  # product name regex to collection identifier
    re.compile(
        r"c_gls_NDVI_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "ndvi_global_1km_10daily_v{version_major}"
}

PRODUCT = {  # dataset name to collection identifier
    re.compile(r"ndvi[_-]"): "vegetation_indices"
}

COMPONENT = {  # components to product types
    "bio-geophysical": {"vegetation_indices"}
}


class LookupSource(MetadataSource):
    """
    Extract metadata information using lookup tables.
    """

    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        if not metadata.dataset_name:
            for regex, value in DATASET.items():
                if match := regex.match(metadata.name):
                    metadata.dataset_name = value.format_map(match.groupdict())
                    break
        metadata.add_attribute(
            "collectionIdentifier", StringAttribute, lambda: metadata.dataset_name
        )
        metadata.add_attribute(
            "collectionShortName",
            StringAttribute,
            lambda: metadata.dataset_name.split("_")[0],
        )  # TODO: check if correct
        if not metadata.product_type:
            for regex, value in PRODUCT.items():
                if match := regex.match(metadata.dataset_name):
                    metadata.product_type = value
                    break
        if not metadata.has_attribute("component"):
            for component, product_types in COMPONENT.items():
                if metadata.product_type in product_types:
                    metadata.add_attribute(
                        "component", StringAttribute, lambda: component
                    )

        if not metadata.spatial_extent:
            metadata.spatial_extent = get_spatial_extent(metadata.dataset_name)

        metadata.add_attribute(
            "nominalResolution",
            IntegerAttribute,
            lambda: get_resolution(metadata.dataset_name),
        )
        metadata.add_attribute(
            name="temporalGrid",
            value_type=StringAttribute,
            factory=lambda: get_temporal_grid(metadata.dataset_name),
        )

        return metadata


def get_resolution(dataset_name: str) -> int | None:
    """
    Derive the resolution from the dataset name.

    :param dataset_name: dataset name
    :return: nominal resolution
    """
    if match := REGEX_RESOLUTION.search(dataset_name):
        factor = 1000 if match.group(2) == "km" else 1
        res_base = float(match.group(1))
        resolution = int(res_base * factor)
        return resolution
    else:
        return None


def get_spatial_extent(dataset_name: str) -> str:
    """
    Derive the spatial extent from the dataset name.

    :param dataset_name: dataset name
    :return: spatial extent as a string
    """
    return dataset_name.split("_")[1]


def get_temporal_grid(dataset_name: str) -> str:
    """
    Derive the temporal grid from the dataset name.

    :param dataset_name: dataset name
    :return:
    """
    temp = dataset_name.split("_")[3]
    # add separator between numbers and unit
    if match := REGEX_NUM_TEMPORAL.match(temp):
        return f"{match.group(1)}-{match.group(2)}"
    return temp
