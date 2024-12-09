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
            temporal_grid_delta = get_relativedelta(
                metadata.get_attribute(attributes.TEMPORAL_GRID).value
            )
            if not matches_temporal_grid(metadata.content_date, temporal_grid_delta):
                logger.info(
                    "Calculating content date from nominal date and temporal grid"
                )
                metadata.content_date = calculate_content_date(
                    metadata.get_attribute(attributes.NOMINAL_DATE).value,
                    temporal_grid_delta,
                )
                logger.info(
                    "Updated content date: {}", metadata.content_date.model_dump()
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


def get_relativedelta(temporal_grid: str) -> relativedelta:
    """
    Get a relativedelta object from the temporal grid.

    :param temporal_grid: temporal grid
    :return: relativedelta object
    """
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


def matches_temporal_grid(
    content_date: ContentDate, temporal_grid: relativedelta
) -> bool:
    """
    Check if the interval between the content date start and end corresponds with the temporal grid.

    :param content_date: ContentDate object
    :param temporal_grid: temporal grid as a relativedelta
    :return:
    """
    logger.debug("Temporal grid delta: {}", temporal_grid)
    delta = relativedelta(
        content_date.end.replace(hour=0, minute=0, second=0, microsecond=0)
        + datetime.timedelta(days=1),
        content_date.start,
    )
    abs_delta = (
        content_date.end.replace(hour=0, minute=0, second=0, microsecond=0)
        + datetime.timedelta(days=1)
        - content_date.start
    )
    logger.debug("Content date delta: {}", delta)
    return delta == temporal_grid or temporal_grid.days + 1 >= abs_delta.days


def calculate_content_date(
    nominal_date: datetime.datetime, temporal_grid: relativedelta
) -> ContentDate:
    """
    Calculate the content date from the nominal date and the temporal grid.
    The content date is assumed to be anchored to a temporal grid starting on the first of the month.
    There are special exceptions for the end of the grid for February and months with 31 days.

    :param nominal_date: nominal date
    :param temporal_grid: temporal grid as relativedelta
    :return: ContentDate object with derived start and end date
    """
    if (nominal_date.day == 1) or (
        temporal_grid.days
        and nominal_date.day % temporal_grid.days == 1
        and not nominal_date.day == 31
    ):
        # assume nominal date as start of content date
        start = nominal_date
        next_anchor = nominal_date + temporal_grid
        if temporal_grid.days:
            if nominal_date.month != next_anchor.month or next_anchor.day == 31:
                # set next anchor to first of the next month
                next_anchor = next_anchor.replace(month=nominal_date.month + 1, day=1)
        end = next_anchor - datetime.timedelta(milliseconds=1)
    else:
        # assume nominal date as end of content date
        prev_anchor = nominal_date + datetime.timedelta(days=1) - temporal_grid
        if temporal_grid.days and prev_anchor.day % temporal_grid.days != 1:
            anchor_count = nominal_date.day // temporal_grid.days
            if nominal_date.day == 31:
                anchor_count -= 1

            prev_anchor = nominal_date.replace(
                day=anchor_count * temporal_grid.days + 1
            )

        start = prev_anchor
        end = nominal_date.replace(hour=23, minute=59, second=59, microsecond=999000)

    return ContentDate(start=start, end=end)
