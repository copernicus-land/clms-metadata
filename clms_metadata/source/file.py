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

from clms_metadata.constants import attributes, lookup_tables
from clms_metadata.models import (
    ContentDate,
    ListStringAttribute,
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
                if not metadata.has_attribute(attributes.PLATFORM_SHORT_NAME):
                    platform_dict = get_platform(tags)
                    platformShortNames = list(platform_dict.keys())
                    platforSerialIdentifiers = [
                        serial for v in platform_dict.values() if v for serial in v
                    ]

                    metadata.add_attribute(
                        name=attributes.PLATFORM_SHORT_NAME
                        if len(platformShortNames) == 1
                        else attributes.PLATFORM_SHORT_NAMES,
                        value_type=StringAttribute
                        if len(platformShortNames) == 1
                        else ListStringAttribute,
                        factory=lambda: platformShortNames[0]
                        if len(platformShortNames) == 1
                        else platformShortNames,
                    )
                    metadata.add_attribute(
                        name=attributes.PLATFORM_SERIAL_IDENTIFIER
                        if len(platforSerialIdentifiers) == 1
                        else attributes.PLATFORM_SERIAL_IDENTIFIERS,
                        value_type=StringAttribute
                        if len(platforSerialIdentifiers) == 1
                        else ListStringAttribute,
                        factory=lambda: platforSerialIdentifiers[0]
                        if len(platforSerialIdentifiers) == 1
                        else platforSerialIdentifiers,
                    )

                instrumentShortNames = [
                    s.strip() for s in tags.get("sensor").split(",")
                ]
                metadata.add_attribute(
                    name=attributes.INSTRUMENT_SHORT_NAME
                    if len(instrumentShortNames) == 1
                    else attributes.INSTRUMENT_SHORT_NAMES,
                    value_type=StringAttribute
                    if len(instrumentShortNames) == 1
                    else ListStringAttribute,
                    factory=lambda: instrumentShortNames[0]
                    if len(instrumentShortNames) == 1
                    else instrumentShortNames,
                )

        return metadata

    def get_processing_center(self, tags: dict) -> str | None:
        """
        Get the processing center information from the raster metadata.

        :param tags: raster data tags
        :return: processing center, if available
        """
        processing_center = tags.get("institution") or tags.get("processing_centre")
        if processing_center is not None:
            processing_center = processing_center.replace(" NV", "").replace(
                " GMBH", ""
            )
        return processing_center

    def _get_info_json(self, path: Path | CloudPath, metadata: Metadata):
        with open(path) as f:
            content = json.load(f)
        properties = content["properties"]
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
            dataset_id = f"wl-lakes_global_vector_daily_v{metadata.get_attribute(attributes.COLLECTION_VERSION)}"
        elif "river" in properties:
            dataset_id = f"wl-rivers_global_vector_daily_v{metadata.get_attribute(attributes.COLLECTION_VERSION)}"
        else:
            raise ValueError

        metadata.add_attribute(
            name=attributes.DATASET_IDENTIFIER,
            value_type=StringAttribute,
            factory=lambda: dataset_id,
        )

        metadata.geometry = content["geometry"]
        metadata.origin_date = properties["updated"]

        metadata.add_attribute(
            name=attributes.PROCESSING_CENTER,
            value_type=StringAttribute,
            factory=lambda: "CLS"
            if (institution := properties["institution"]) == "LEGOS, CLS, CNES"
            else institution.split(",")[0].upper(),
        )


def get_platform(tags: dict) -> dict[str, list[str] | None]:
    """
    Get the platform information from the 'platform' tag in the raster metadata.
    Returns a tuple of platformShortName and platformSerialIdentifier.

    :param tags: raster metadata tags
    :return: platform information
    """
    platformstr = tags.get("platform")
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

    # turn platformstr into a map of platformShortName to platformSerialIdentifiers
    platforms = {p.strip(): None for p in platformstr.split(",")}

    # Support for "AND" between platform names or platform serials
    # e.g. "SENTINEL-3A AND SENTINEL-3B" or "SENTINEL 3 (A AND B)"
    bracket_serials_regex = r"\(([A-Z]) AND ([A-Z])\)"
    if " AND " in platformstr:
        # repl_platforms = {}
        for platf in list(platforms):
            if regex_match_part := re.search(bracket_serials_regex, platf):
                platforms.pop(platf)
                (platform_short, platformserial) = platf.split(" (")
                platform_short = platform_short.replace(" ", "-")
                platforms[platform_short] = platforms.get(platform_short, list()) + [
                    serial for serial in regex_match_part.groups()
                ]
            elif " AND " in platf:
                serials = platforms.pop(platf)
                platforms.update({p: serials for p in platf.split(" AND ")})

    # Support for SSM/SWI multi-mission products with eg "METOP B+C"
    if "+" in platformstr:
        for platf in list(platforms):
            if "+" in platf:
                platforms.pop(platf)
                (platform_short, platformserial) = platf.split(" ")
                split_serial = platformserial.split("+")
                platforms[platform_short] = (
                    platforms.get(platform_short, list()) + split_serial
                )

    # We covered the AND and + syntaxes, all remaining spaces are between platforms
    # with exception of "SUOMI NPP" or "METOP X"
    metop_regex = re.compile(r"(METOP)[ -]?([A-Z])")
    for platf in list(platforms):
        if "SUOMI NPP" == platf:
            continue
        elif match := metop_regex.match(platf):
            platforms.pop(platf)
            platform_short, serial = match.groups()
            platforms[platform_short] = platforms.get(platform_short, list()) + [serial]
        elif " " in platf:
            platforms.pop(platf)
            platforms.update({p: None for p in platf.split(" ")})

    # Support for LST, eg MSG4 -> MSG-4
    lst_regex = re.compile(r"(MSG|MTSAT|HIMAWARI|GOES)([0-9]+|E|R)")

    # Hyphenate SENTINELs, eg SENTINEL3A => SENTINEL-3A
    # and extract serial identifier
    sentinel_regex = re.compile(r"(SENTINEL)-?(\d+)([A-Z]+)")
    ignore = ("N/A", "PLATFORM")

    for platf in list(platforms):
        if match := lst_regex.match(platf):
            platforms.pop(platf)
            platform_short, suffix = match.groups()
            platform = f"{platform_short}-{suffix}"
            platforms[platform] = platforms.get(platform, None)
        if match := sentinel_regex.match(platf):
            platforms.pop(platf)
            base, num, serial = match.groups()
            platform_short = f"{base}-{num}"
            platforms[platform_short] = platforms.get(platform_short, list()) + [serial]
        if platf in ignore:
            platforms.pop(platf)
    if platforms == {}:
        if mapped_platform := lookup_tables.SENSOR_PLATFORM_MAPPING.get(
            tags.get("sensor", "")
        ):
            platforms[mapped_platform] = None
    return platforms
