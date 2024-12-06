import datetime
import re
from pathlib import Path

from cloudpathlib import CloudPath
from dateutil.relativedelta import relativedelta
from loguru import logger

from clms_metadata.constants import attributes
from clms_metadata.models import (
    ContentDate,
    IntegerAttribute,
    Metadata,
    StringAttribute,
)
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
        r"c_gls_FAPAR300-RT\d_\d{12}_[A-Z0-9-]+_[A-Z0-9-]+_V(?P<version>(?P<version_major>\d).\d.\d)"
    ): "fapar_global_300m_10daily_v{version_major}",
}

PRODUCT = {  # dataset name to collection identifier
    re.compile(r"ndvi[_-]"): "vegetation_indices",
    re.compile(r"g?dmp[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"(fapar|fcover|lai)[_-]"): "vegetation_properties",
}

COMPONENT = {  # components to product types
    "bio-geophysical": {
        "vegetation_indices",
        "dry-gross_dry_matter_productivity",
        "vegetation_properties",
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

        if metadata.has_attribute(attributes.CONSOLIDATION_PERIOD):
            temporal_grid = metadata.get_attribute(attributes.TEMPORAL_GRID).value
            temporal_grid_delta = get_relativedelta(temporal_grid)
            logger.debug("Temporal grid delta: {}", temporal_grid_delta)
            content_date_delta = relativedelta(
                metadata.content_date.end.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                + datetime.timedelta(days=1),
                metadata.content_date.start,
            )
            logger.debug("Content date delta: {}", content_date_delta)
            if not temporal_grid_delta == content_date_delta:
                # calculate content date from nominal date
                nominal_date = metadata.get_attribute(attributes.NOMINAL_DATE).value
                if (
                    nominal_date.day % 10 == 1
                ):  # assume nominal date as start of content date
                    start = nominal_date
                    end = (
                        nominal_date
                        + temporal_grid_delta
                        - datetime.timedelta(milliseconds=1)
                    )
                else:  # assume nominal date as end of content date
                    start = (
                        nominal_date - temporal_grid_delta + datetime.timedelta(days=1)
                    )
                    end = nominal_date.replace(
                        hour=23, minute=59, second=59, microsecond=999000
                    )
                metadata.content_date = ContentDate(start=start, end=end)

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


def get_relativedelta(temporal_grid: str) -> relativedelta:
    if temporal_grid == "daily":
        return relativedelta(days=1)
    if m := re.match(r"(\d+)-daily", temporal_grid):
        return relativedelta(days=int(m.group(1)))
    if temporal_grid == "monthly":
        return relativedelta(months=1)
    if m := re.match(r"(\d+)-monthly", temporal_grid):
        return relativedelta(months=int(m.group(1)))
    if temporal_grid == "yearly":
        return relativedelta(years=1)
    if m := re.match(r"(\d+)-yearly", temporal_grid):
        return relativedelta(years=int(m.group(1)))
