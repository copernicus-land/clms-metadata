import datetime
import re
from pathlib import Path
from typing import Optional

from cloudpathlib import CloudPath
from dateutil.relativedelta import relativedelta
from loguru import logger

from clms_metadata.constants import attributes, lookup_tables, regex
from clms_metadata.constants.content_type import FILE_FORMAT_GEOJSON
from clms_metadata.constants.lookup_tables import (
    COMPONENT_TO_PRODUCT_TYPES,
    DATASET_SHORT_NAMES,
    SPATIAL_EXTENT_MAPPING,
)
from clms_metadata.models import (
    ContentDate,
    IntegerAttribute,
    Metadata,
    StringAttribute,
)
from clms_metadata.source import MetadataSource


class LookupSource(MetadataSource):
    """
    Extract metadata information using lookup tables.
    """

    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        super().get_info(product_files, metadata)
        if not metadata.dataset_identifier and (
            dataset_identifier := self.extract_collection_id(file_name=metadata.name)
        ):
            metadata.dataset_identifier = dataset_identifier

        metadata.add_attribute(
            name=attributes.DATASET_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: part
            if (part := metadata.dataset_identifier.split("_")[0])
            in DATASET_SHORT_NAMES
            else self.lookup_short_name(metadata.dataset_identifier),
        )  # TODO: check if correct
        metadata.add_attribute(
            name=attributes.DATASET_ALIAS,
            value_type=StringAttribute,
            factory=lambda: metadata.dataset_identifier[
                : metadata.dataset_identifier.rfind("_")
            ],
        )

        if not metadata.product_type:
            metadata.product_type = self.determine_product_type(
                metadata.dataset_identifier
            )
        if not metadata.component:
            for component, product_types in COMPONENT_TO_PRODUCT_TYPES.items():
                if metadata.product_type in product_types:
                    metadata.component = component
                    break

        metadata.add_attribute(
            name=attributes.AREA_OF_INTEREST,
            value_type=StringAttribute,
            factory=lambda: get_spatial_extent(metadata.dataset_identifier),
        )

        metadata.add_attribute(
            attributes.METRIC_GRID_SPACING,
            IntegerAttribute,
            lambda: get_resolution(metadata.dataset_identifier),
        )
        metadata.add_attribute(
            name=attributes.GRID_LABEL,
            value_type=StringAttribute,
            factory=lambda: match.group(1)
            if (match := regex.RESOLUTION.search(metadata.dataset_identifier))
            else None,
        )
        metadata.add_attribute(
            name=attributes.TEMPORAL_REPEAT_RATE,
            value_type=StringAttribute,
            factory=lambda: get_temporal_grid(metadata.dataset_identifier),
        )

        if (
            metadata.get_attribute(attributes.FILE_FORMAT).value != FILE_FORMAT_GEOJSON
            and not regex.DATASET_NDVI_STATISTICS.match(metadata.dataset_identifier)
            and not regex.DATASET_SWI_STATIC.match(metadata.dataset_identifier)
        ):
            temporal_grid_delta = get_relativedelta(
                metadata.get_attribute(attributes.TEMPORAL_REPEAT_RATE).value
            )
            if not matches_temporal_grid(metadata.content_date, temporal_grid_delta):
                logger.info(
                    "Calculating content date from nominal date and temporal grid"
                )
                metadata.content_date = calculate_content_date(
                    metadata.nominal_date,
                    temporal_grid_delta,
                )
                logger.info(
                    "Updated content date: {}", metadata.content_date.model_dump()
                )

        if not metadata.has_attribute(
            attributes.MISSION_SHORT_NAME
        ) and metadata.has_attribute(attributes.INSTRUMENT_SHORT_NAME):
            metadata.add_attribute(
                name=attributes.MISSION_SHORT_NAME,
                value_type=StringAttribute,
                factory=lambda: lookup_tables.INSTRUMENT_MISSION_MAPPING.get(
                    metadata.get_attribute(attributes.INSTRUMENT_SHORT_NAME).value, None
                ),
            )

        if m := regex.SWI_STATIC.match(metadata.name):
            metadata.add_attribute(
                name=attributes.SWI_SUB_PARAMETER,
                value_type=StringAttribute,
                factory=lambda: m.group(attributes.SWI_SUB_PARAMETER),
            )
        if m := regex.SWI_TIMESERIES.match(metadata.name):
            metadata.add_attribute(
                name=attributes.SWI_TS_CELL_ID,
                value_type=StringAttribute,
                factory=lambda: m.group(attributes.SWI_TS_CELL_ID),
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
        try:
            match: re.Match
            template: str
            [(match, template)] = [
                (_match, _template)
                for _regex, _template in lookup_tables.PRODUCT_NAME_TO_DATASET.items()
                if (_match := _regex.match(file_name))
            ]
            return template.format_map(match.groupdict()).lower()
        except ValueError as e:
            logger.error(
                "Cannot extract dataset identifier from product identifier {}",
                file_name,
            )
            logger.error("Exception: {}", repr(e))
            raise ValueError(
                f"No collection regex match was found for filename {file_name}"
            ) from e

    @staticmethod
    def determine_product_type(collection_id: str) -> Optional[str]:
        """
        Look for a match on the product identifier to map to the corresponding product type
        :param collection_id: The identifier of the collection
        :return: The product type of the collection if a match is found, None otherwise
        """
        try:
            [product_type] = [
                _pt
                for _regex, _pt in lookup_tables.DATASET_TO_PRODUCT_TYPE.items()
                if _regex.match(collection_id)
            ]
            return product_type
        except ValueError as e:
            logger.error(
                "Cannot determine product type from collection identifier {}",
                collection_id,
            )
            logger.error("Exception: {}", repr(e))

    @staticmethod
    def lookup_short_name(dataset_identifier: str) -> Optional[str]:
        """
        Look for the dataset short name based on the dataset identifier.
        :param dataset_identifier: dataset identifier
        :return: dataset short name iff a match is found, None otherwise
        """
        try:
            [dataset_short_name] = [
                _dsn
                for _regex, _dsn in lookup_tables.DATASET_NAME_TO_SHORT_NAME.items()
                if _regex.match(dataset_identifier)
            ]
            return dataset_short_name
        except ValueError as e:
            logger.error(
                "Cannot get short datasetShortName for dataset {}", dataset_identifier
            )
            logger.error("Exception: {}", repr(e))


def get_resolution(collection_identifier: str) -> int | None:
    """
    Derive the resolution from the collection identifier.

    :param collection_identifier: collection identifier
    :return: nominal resolution
    """
    if match := regex.RESOLUTION.search(collection_identifier):
        factor = 1000 if match.group(3) == "km" else 1
        res_base = float(match.group(2))
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
    spatial_extent = collection_identifier.split("_")[1]
    if mapped_value := SPATIAL_EXTENT_MAPPING.get(spatial_extent):
        spatial_extent = mapped_value
    return spatial_extent


def get_temporal_grid(collection_identifier: str) -> str:
    """
    Derive the temporal grid from the dataset name.

    :param collection_identifier: dataset name
    :return:
    """
    temp = collection_identifier.split("_")[3]
    return temp


def get_relativedelta(temporal_grid: str) -> relativedelta:
    """
    Get a relativedelta object from the temporal grid.

    :param temporal_grid: temporal grid
    :return: relativedelta object
    """
    if temporal_grid == "daily":
        return relativedelta(days=1)
    if m := re.match(r"(\d+)daily", temporal_grid):
        return relativedelta(days=int(m.group(1)))
    if temporal_grid == "monthly":
        return relativedelta(months=1)
    if m := re.match(r"(\d+)monthly", temporal_grid):
        return relativedelta(months=int(m.group(1)))
    if temporal_grid == "yearly":
        return relativedelta(years=1)
    if m := re.match(r"(\d+)yearly", temporal_grid):
        return relativedelta(years=int(m.group(1)))
    if temporal_grid == "hourly":
        return relativedelta(hours=1)
    if m := re.match(r"(\d+)hourly", temporal_grid):
        return relativedelta(hours=int(m.group(1)))

    raise ValueError(f"Unknown temporal grid: {temporal_grid}")


def matches_temporal_grid(
    content_date: ContentDate, temporal_grid: relativedelta
) -> bool:
    """
    Check if the interval between the content date start and end corresponds with the temporal grid.

    First, an exact match of the interval delta and the temporal grid is checked.
    Then, the following edge cases are also considered:
      - the content date interval is 1 day longer than the temporal grid (e.g. month with 31 days)
      - the content date interval is shorter than the temporal grid (e.g. the end of the month February)

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


def get_platform_acronym(platform_short_name: str) -> str:
    """
    Extract the platform acronym from the platform short name.
    Currently, only the behaviour for Sentinel platforms is defined.
    In all other cases, the original platform short name is returned.

    :param platform_short_name: platform short name
    :return: platform acronym
    """
    if m := regex.SENTINEL_NUM_SERIAL.match(platform_short_name):
        return f"S{m.group(2)}{m.group(3)}"
    else:
        return platform_short_name
