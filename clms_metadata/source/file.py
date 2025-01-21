import json
import re
from pathlib import Path

import rasterio
import rasterio.warp
import rioxarray
import shapely.geometry
from cloudpathlib import CloudPath
from loguru import logger
from overrides import overrides

from clms_metadata.constants import attributes, lookup_tables, regex
from clms_metadata.models import (
    ContentDate,
    IntegerAttribute,
    Metadata,
    StringAttribute,
)
from clms_metadata.source.base import MetadataSource


class FileSource(MetadataSource):
    """Retrieve metadata from the file content."""

    @overrides
    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        super().get_info(product_files, metadata)
        for path in product_files:
            if path.suffix.lower() in (".nc", ".tiff", ".tif"):
                metadata = self._get_info_raster(path, metadata)
            if path.suffix.lower() in (".json", ".geojson"):
                metadata = self._get_info_json(path, metadata)

        return metadata

    def _get_info_raster(self, path: Path | CloudPath, metadata: Metadata) -> Metadata:
        with self.storage.rasterio_env():
            # with rioxarray.open_rasterio(str(path)) as data:
            # use rasterio directly to work around issue https://github.com/corteva/rioxarray/issues/829
            with rasterio.open(str(path)) as data:
                tags = rioxarray._io._parse_tags(data.tags())
                logger.debug(tags)
                if data.subdatasets:
                    with rasterio.open(
                        data.subdatasets[0], transform=data.transform
                    ) as sub_data:
                        bounds = (
                            rasterio.warp.transform_bounds(
                                sub_data.crs, "EPSG:4326", *sub_data.bounds
                            )
                            if sub_data.crs
                            else sub_data.bounds
                        )
                else:
                    bounds = (
                        rasterio.warp.transform_bounds(
                            data.crs, "EPSG:4326", *data.bounds
                        )
                        if data.crs
                        else data.bounds
                    )
                if not metadata.content_date:
                    metadata.content_date = ContentDate(
                        start=tags["time_coverage_start"],
                        end=tags["time_coverage_end"],
                    )
                if not metadata.geometry:
                    # TODO: check if half-pixel shift is needed?
                    metadata.geometry = shapely.set_precision(
                        shapely.geometry.box(*bounds),
                        grid_size=self.settings.geometry.precision,
                    )
                metadata.add_attribute(
                    name=attributes.PROCESSING_CENTER,
                    value_type=StringAttribute,
                    factory=lambda: self.get_processing_center(tags),
                )
                metadata = set_platform(tags.get("platform"), metadata)

                metadata.add_attribute(
                    name=attributes.INSTRUMENT_SHORT_NAME,
                    value_type=StringAttribute,
                    factory=lambda: ",".join(parse_sensor(tags.get("sensor"))) or None,
                )
                if not metadata.dataset_identifier and (
                    dataset_identifier := get_dataset_identifier_from_identifier_tag(
                        tags.get("identifier")
                    )
                ):
                    metadata.dataset_identifier = dataset_identifier

                if (
                    not metadata.has_attribute(attributes.CONSOLIDATION_PERIOD)
                    and (processing_mode := tags.get("processing_mode"))
                    and processing_mode.lower() == "consolidated"
                    and not regex.CONSOLIDATION.search(tags.get("identifier"))
                ):
                    logger.info(
                        "Consolidated product without explicit RT in product identifier, adding consolidationPeriod=6"
                    )
                    metadata.add_attribute(
                        name=attributes.CONSOLIDATION_PERIOD,
                        value_type=IntegerAttribute,
                        factory=lambda: 6,
                    )

        return metadata

    def get_processing_center(self, tags: dict) -> str | None:
        """
        Get the processing center information from the raster or vector metadata.

        :param tags: metadata tags
        :return: processing center, if available
        """
        processing_center = tags.get("institution") or tags.get("processing_centre")
        if processing_center is not None:
            processing_center = processing_center.replace(" NV", "").replace(
                " GMBH", ""
            )
        if processing_center == "LEGOS, CLS, CNES":
            processing_center = "CLS"

        processing_center = ",".join(pc.strip() for pc in processing_center.split(","))

        return processing_center

    def _get_info_json(self, path: Path | CloudPath, metadata: Metadata):
        with open(path) as f:
            content = json.load(f)
        properties = content["properties"]
        logger.debug(properties)
        if (
            not metadata.content_date
            and "time_coverage_start" in properties
            and "time_coverage_end" in properties
        ):
            metadata.content_date = ContentDate(
                start=properties["time_coverage_start"],
                end=properties["time_coverage_end"],
            )

        if "lake" in properties:
            dataset_id = f"wl-lakes_global_vector_daily_v{metadata.get_attribute(attributes.DATASET_VERSION).value}"
            metadata.add_attribute(
                name=attributes.WATER_LEVEL_LAKE_NAME,
                value_type=StringAttribute,
                factory=lambda: properties.get("lake"),
            )
        elif "river" in properties:
            dataset_id = f"wl-rivers_global_vector_daily_v{metadata.get_attribute(attributes.DATASET_VERSION).value}"
            metadata.add_attribute(
                name=attributes.WATER_LEVEL_RIVER_NAME,
                value_type=StringAttribute,
                factory=lambda: properties.get("river"),
            )
        else:
            dataset_id = None
            logger.warning("Cannot determine dataset ID based on JSON properties")

        if not metadata.dataset_identifier and dataset_id:
            metadata.dataset_identifier = dataset_id

        metadata.add_attribute(
            name=attributes.WATER_LEVEL_BASIN_NAME,
            value_type=StringAttribute,
            factory=lambda: properties.get("basin"),
        )

        metadata.geometry = content["geometry"]
        metadata.origin_date = properties["updated"]

        metadata.add_attribute(
            name=attributes.PROCESSING_CENTER,
            value_type=StringAttribute,
            factory=lambda: self.get_processing_center(properties),
        )

        metadata = set_platform(properties.get("platform"), metadata)
        metadata.add_attribute(
            name=attributes.INSTRUMENT_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: ",".join(parse_sensor(properties.get("sensor"))) or None,
        )

        return metadata


def set_platform(platformstr: str | None, metadata: Metadata) -> Metadata:
    """
    Set the platform information on the metadata object.

    :param platformstr: platform string
    :param metadata: metadata object
    :return: updated metadata object
    """
    if platformstr is None:
        platform_dict = dict()
    else:
        platform_dict = parse_platform(platformstr)
    missionShortNames = list(platform_dict.keys())
    platformShortNames = [serial for v in platform_dict.values() if v for serial in v]

    metadata.add_attribute(
        name=attributes.MISSION_SHORT_NAME,
        value_type=StringAttribute,
        factory=lambda: ",".join(missionShortNames) or None,
    )

    metadata.add_attribute(
        name=attributes.PLATFORM_SHORT_NAME,
        value_type=StringAttribute,
        factory=lambda: ",".join(platformShortNames) or None,
    )

    metadata.add_attribute(
        name=attributes.PLATFORM_ACRONYM,
        value_type=StringAttribute,
        factory=lambda: ",".join(
            acronym
            for platform_short_name in platformShortNames
            if (
                acronym := regex_lookup(
                    lookup_tables.PLATFORM_SHORT_NAME_TO_ACRONYM, platform_short_name
                )
            )
        )
        or None,
    )

    return metadata


def build_platform_short_name(
    mission_short_name: str, serial: str | None
) -> str | None:
    if regex.SENTINEL_OR_METOP.match(mission_short_name) and serial:
        return mission_short_name + serial


def regex_lookup(lookup_dict: dict[re.Pattern, str], key: str) -> str | None:
    for lookup_regex, template in lookup_dict.items():
        if match := lookup_regex.match(key):
            return template.format_map(match.groupdict())


def parse_platform(platformstr: str) -> dict[str, list[str] | None]:
    """
    Get the platform information from the 'platform' metadata string.
    Returns a dictionary of missionShortName to platformShortName.

    :param platformstr: platform metadata string
    :return: platform information
    """
    platformstr = (
        platformstr.upper().replace("_", "-").replace("SUOMI-NPP", "SUOMI NPP").strip()
    )

    # support for platforms with LIE 250m with old name for TERRA/AQUA/NOAA-20
    # TERRA (EOS AM-1) => [TERRA]
    if (
        any(modis in platformstr for modis in ["AQUA", "TERRA", "NOAA-20"])
        and " (" in platformstr
    ):
        platformstr = platformstr.split(" (")[0]

    # turn platformstr into a map of missionShortName to platformShortName
    platforms: dict[str, list[str] | None] = {
        p.strip(): None for p in platformstr.split(",")
    }

    # rewrite missionShortName to strip hyphens
    platforms = {p.replace("-", ""): None for p in platforms}

    # Support for "AND" between platform names or platform serials
    # e.g. "SENTINEL-3A AND SENTINEL-3B" or "SENTINEL 3 (A AND B)"
    if " AND " in platformstr:
        for mission in list(platforms):
            if regex_match_part := regex.PLATFORM_SERIALS_AND.search(mission):
                platforms.pop(mission)
                (mission, platformserial) = mission.split(" (")
                mission = mission.replace(" ", "")  # TODO: can be removed?
                platforms[mission] = platforms.get(mission, list()) + [
                    build_platform_short_name(mission, serial)
                    for serial in regex_match_part.groups()
                ]
            elif " AND " in mission:
                serials = platforms.pop(mission)
                platforms.update({p: serials for p in mission.split(" AND ")})

    # Support for SSM/SWI multi-mission products with eg "METOP B+C"
    if "+" in platformstr:
        for mission in list(platforms):
            if "+" in mission:
                platforms.pop(mission)
                (mission, platformserial) = mission.split(" ")
                split_serial = platformserial.split("+")
                platforms[mission] = platforms.get(mission, list()) + [
                    build_platform_short_name(mission, serial)
                    for serial in split_serial
                ]

    # We covered the AND and + syntaxes, all remaining spaces are between platforms
    # with exception of "SUOMI NPP" or "METOP X"
    for mission in list(platforms):
        if "SUOMI NPP" == mission:
            continue
        elif match := regex.METOP.match(mission):
            platforms.pop(mission)
            mission, serial = match.groups()
            platforms[mission] = platforms.get(mission, list()) + [
                build_platform_short_name(mission, serial)
            ]
        elif " " in mission:
            platforms.pop(mission)
            platforms.update({p: None for p in mission.split(" ")})

    ignore = ("N/A", "PLATFORM", "GLDASNOAH")

    for mission in list(platforms):
        if match := regex.GOES.match(mission):
            platforms.pop(mission)
            mission, suffix = match.groups()
            platforms[mission] = platforms.get(mission, list()) + [f"{mission}{suffix}"]
        elif match := regex.MSG.match(mission):
            # rewrite MSG to METEOSAT
            platforms.pop(mission)
            base, num = match.groups()
            num = int(num) + 7
            mission = f"METEOSAT{num}"
            platforms[mission] = [mission]
        elif match := regex.SENTINEL_NUM_SERIAL.match(mission):
            platforms.pop(mission)
            base, num, serial = match.groups()
            mission = f"{base}{num}"
            platforms[mission] = platforms.get(mission, list()) + [
                build_platform_short_name(mission, serial)
            ]
        elif mission in ignore:
            platforms.pop(mission)

        # try to add missing info
        if mission in platforms and platforms[mission] is None:
            platform_short_name = regex_lookup(
                lookup_tables.MISSION_TO_PLATFORM, mission
            )
            if platform_short_name:
                platforms[mission] = [platform_short_name]
    return platforms


def parse_sensor(sensor_tag: str | None) -> list[str]:
    """
    Parse the sensor tag in the product metadata.

    :param sensor_tag: sensor tag embedded in the product
    :return: a list of sensor strings
    """
    if sensor_tag is None:
        return []
    sensors = [s.strip() for s in sensor_tag.split(",")]

    for i, s in enumerate(sensors):
        if match := regex.NAME_WITH_SHORT_NAME_IN_BRACKETS.match(s):
            # if the long and short name are in the tag, extract the short name
            sensors[i] = match.group(1)
        if match := regex.SENSOR_SPOT_VEGETATION.match(s):
            # if the sensor name has VEGETATION with a number suffix, only take VEGETATION
            sensors[i] = match.group(1)
        if match := regex.SENSOR_SENTINEL3_SLSTR.match(s):
            # if the sensor name has SLSTR with a suffix, only take SLSTR
            sensors[i] = match.group(1)

    return sensors


def get_dataset_identifier_from_identifier_tag(identifier: str | None) -> str | None:
    """
    Extract the dataset identifier based on the identifier tag embedded in the product metadata.

    When encountering exceptions None is returned so the "lookup" logic can still try to find a match.
    :param identifier: the identifier tag embedded in the product
    :return: the dataset identifier if it can be derived, None otherwise
    """
    try:
        if not identifier:
            raise (ValueError("No identifier found in raster metadata"))

        identifier_parts = identifier.split(":")
        parent_identifier = identifier_parts[-2]
        [(match, template)] = [
            (match, dataset_id_template)
            for regex_id, dataset_id_template in lookup_tables.IDENTIFIER_TAG_DATASET_IDENTIFIER_MAPPING.items()
            if (match := regex_id.match(parent_identifier))
        ]
        dataset_identifier = template.format_map(match.groupdict())

        logger.debug(
            "Extracted dataset identifier {} from {}", dataset_identifier, identifier
        )
    except (IndexError, KeyError, re.error, ValueError, AttributeError) as e:
        logger.warning(
            f"Could not extract dataset identifier from {identifier} due to {repr(e)}"
        )
        return None

    return dataset_identifier
