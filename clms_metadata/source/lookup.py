import datetime
import re
from pathlib import Path
from typing import Optional

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

PRODUCT = {  # dataset name to collection identifier
    re.compile(r"ndvi[_-]"): "vegetation_indices",
    re.compile(r"g?dmp[_-]"): "dry-gross_dry_matter_productivity",
    re.compile(r"(fapar|fcover|lai)[_-]"): "vegetation_properties",
    re.compile(r"^sce"): "snow_cover_extent",
    re.compile(r"^swe"): "snow_water_equivalent",
    re.compile(r"^lswt"): "land_surface_temperature",
    re.compile(r"^wb"): "water_bodies",
    re.compile(r"^lwq"): "lake_water_quality",
    re.compile(r"^lie"): "river_and_lake_ice_extent",
}

COMPONENT = {  # components to product types
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
            if collection_identifier := self.extract_collection_id(
                file_name=metadata.name
            ):
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
            name=attributes.AREA_OF_INTEREST,
            value_type=StringAttribute,
            factory=lambda: get_spatial_extent(collection_identifier),
        )

        metadata.add_attribute(
            attributes.METRIC_GRID_SPACING,
            IntegerAttribute,
            lambda: get_resolution(collection_identifier),
        )
        metadata.add_attribute(
            name=attributes.GRID_LABEL,
            value_type=StringAttribute,
            factory=lambda: collection_identifier.split("_")[2],
        )
        metadata.add_attribute(
            name=attributes.TEMPORAL_REPEAT_RATE,
            value_type=StringAttribute,
            factory=lambda: get_temporal_grid(collection_identifier),
        )

        if metadata.has_attribute(attributes.CONSOLIDATION_PERIOD):
            temporal_grid_delta = get_relativedelta(
                metadata.get_attribute(attributes.TEMPORAL_REPEAT_RATE).value
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
        raise ValueError(
            f"No collection regex match was found for filename {file_name}"
        )

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
