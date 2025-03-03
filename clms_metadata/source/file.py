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
from clms_metadata.models.metadata import (
    ContentDate,
    IntegerAttribute,
    Metadata,
    StringAttribute,
)
from clms_metadata.models.name_list import EOAssetNameList
from clms_metadata.source.base import MetadataSource
from clms_metadata.util import unique_list

EPSG_4326 = rasterio.crs.CRS.from_epsg(4326)


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
            path_ds = str(path)
            if self.settings.vsicached and isinstance(path, Path):
                path_ds = f"/vsicached?file={path}"
            with rasterio.open(path_ds) as data:
                tags = rioxarray._io._parse_tags(data.tags())
                logger.debug(tags)
                if not metadata.content_date:
                    if "time_coverage_start" in tags:
                        metadata.content_date = ContentDate(
                            start=tags["time_coverage_start"],
                            end=tags["time_coverage_end"],
                        )
                    else:
                        logger.warning(
                            "No time coverage in raster tags, using nominal date '{}' as content date",
                            metadata.nominal_date,
                        )
                        metadata.content_date = ContentDate(
                            start=metadata.nominal_date,
                            end=metadata.nominal_date,
                        )
                if not metadata.geometry:
                    # TODO: check if half-pixel shift is needed?
                    bounds = get_raster_bounds(data, tags)
                    metadata.geometry = shapely.set_precision(
                        shapely.geometry.box(*bounds),
                        grid_size=self.settings.geometry.precision,
                    )
                metadata.add_attribute(
                    name=attributes.PROCESSING_CENTER,
                    value_type=StringAttribute,
                    factory=lambda: get_processing_center(tags),
                )
                metadata = self.set_platform(tags.get("platform"), metadata)

                metadata.add_attribute(
                    name=attributes.INSTRUMENT_SHORT_NAME,
                    value_type=StringAttribute,
                    factory=lambda: ",".join(
                        sensor if sensor else self.settings.unspecified
                        for sensor in parse_sensor(
                            tags.get("sensor"), self.eo_asset_name_list
                        )
                    )
                    or None,
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
            factory=lambda: get_processing_center(properties),
        )

        metadata = self.set_platform(properties.get("platform"), metadata)
        metadata.add_attribute(
            name=attributes.INSTRUMENT_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: ",".join(
                sensor if sensor else self.settings.unspecified
                for sensor in parse_sensor(
                    properties.get("sensor"), self.eo_asset_name_list
                )
            )
            or None,
        )

        return metadata

    def set_platform(self, platformstr: str | None, metadata: Metadata) -> Metadata:
        """
        Set the platform information on the metadata object.

        :param platformstr: platform string
        :param metadata: metadata object
        :return: updated metadata object
        """
        if platformstr is None:
            platform_dict = dict()
        else:
            platform_dict = parse_platform(platformstr, self.eo_asset_name_list)
        missionShortNames = list(
            k if k else self.settings.unspecified for k in platform_dict.keys()
        )
        platformShortNames = [
            serial for v in platform_dict.values() if v for serial in v
        ]

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
                map(
                    lambda v: v if v else self.settings.unspecified,
                    unique_list(
                        platform_acronym
                        if (
                            platform_acronym := self.eo_asset_name_list.lookup(
                                mission=mission_short_name, platform=platform_short_name
                            ).get(attributes.PLATFORM_ACRONYM)
                        )
                        != self.settings.unspecified
                        else None
                        for mission_short_name, platform_short_names in platform_dict.items()
                        for platform_short_name in platform_short_names or []
                    ),
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


def parse_platform(
    platformstr: str, eo_asset_name_list: EOAssetNameList
) -> dict[str | None, list[str] | None]:
    """
    Get the platform information from the 'platform' metadata string.
    Returns a dictionary of missionShortName to platformShortName.

    :param platformstr: platform metadata string
    :return: platform information
    """
    platformstr = platformstr.upper().replace("_", "-").strip()
    platformstr = re.sub(r"SUOMI[-_ ]NPP", "SUOMINPP", platformstr, flags=re.IGNORECASE)

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
    # with exception of "METOP X"
    for mission in list(platforms):
        if match := regex.METOP.match(mission):
            platforms.pop(mission)
            mission, serial = match.groups()
            platforms[mission] = platforms.get(mission, list()) + [
                build_platform_short_name(mission, serial)
            ]
        elif " " in mission:
            platforms.pop(mission)
            platforms.update({p: None for p in mission.split(" ")})

    for mission in list(platforms):
        if match := regex.GOES.match(mission):
            platforms.pop(mission)
            mission, suffix = match.groups()
            names = [f"{mission}{suffix}"] if suffix else list()
            platforms[mission] = platforms.get(mission, list()) + names
        elif match := regex.MSG.match(mission):
            # rewrite MSG to METEOSAT
            platforms.pop(mission)
            base, num = match.groups()
            num = int(num) + 7
            mission = f"METEOSAT{num}"
            platforms[mission] = [mission]
        elif match := (
            regex.SENTINEL_NUM_SERIAL.match(mission)
            or regex.SENTINEL_SHORT_NUM_SERIAL.match(mission)
        ):
            platforms.pop(mission)
            base, num, serial = match.groups()
            mission = f"SENTINEL{num}"
            platforms[mission] = platforms.get(mission, list()) + [
                build_platform_short_name(mission, serial)
            ]
        elif mission not in eo_asset_name_list.missionShortNames:
            platforms.pop(mission)
            platforms[None] = None
            continue

        # try to add missing info
        if mission is not None and platforms[mission] is None:
            result = eo_asset_name_list.lookup(mission=mission)
            if platform_short_name := result.get(attributes.PLATFORM_SHORT_NAME):
                platforms[mission] = [platform_short_name]
    return platforms


def parse_sensor(
    sensor_tag: str | None, eo_asset_name_list: EOAssetNameList
) -> list[str]:
    """
    Parse the sensor tag in the product metadata.

    :param sensor_tag: sensor tag embedded in the product
    :param eo_asset_name_list: list of supported EO asset names
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
        if regex.SENSOR_SENTINEL1_SAR.match(s):
            sensors[i] = "SAR"

    sensors = unique_list(
        s if s in eo_asset_name_list.instrumentShortNames else None for s in sensors
    )
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


def get_raster_bounds(
    ds: rasterio.DatasetReader, tags: dict
) -> tuple[float, float, float, float]:
    """
    Get the bounds of a raster dataset.


    A few options are considered to extract the bounds:
        * bounds reported by rasterio
        * bounds of a subdataset reported by rasterio
        * bounds constructed from the geospatial_lon/lat_min/max tags
        * calculating bounds from netCDF lon/lat variables

    :param ds: raster dataset
    :param tags: raster metadata tags
    :return: bounds as a tuple (left, bottom, right, top)
    """
    bounds: tuple[float, float, float, float]
    if ds.crs:
        # get bounds of the raster directly
        bounds = rasterio.warp.transform_bounds(ds.crs, EPSG_4326, *ds.bounds)
        logger.debug("Bounds from raster: {}", bounds)
        if is_bounds_plausible(bounds):
            return bounds
        else:
            logger.warning("Bounds {} are not plausible", bounds)
    if ds.transform != rasterio.transform.Affine.identity():
        logger.debug(
            "Ignoring (missing) CRS in dataset. Using bounds as-is, assuming EPSG:4326."
        )
        bounds = ds.bounds
        logger.debug("Bounds from dataset: {}", bounds)
        if is_bounds_plausible(bounds):
            return bounds
        else:
            logger.warning("Bounds {} are not plausible", bounds)
    else:
        logger.debug("No CRS or transform in dataset {}", ds.name)

    if ds.subdatasets:
        # get bounds of a subdataset
        logger.debug("Opening subdataset {}", ds.subdatasets[0])
        with rasterio.open(ds.subdatasets[0]) as sub_ds:
            bounds = get_raster_bounds(sub_ds, tags)
            if bounds:
                return bounds

    if all(
        t in tags
        for t in (
            "geospatial_lat_min",
            "geospatial_lat_max",
            "geospatial_lon_min",
            "geospatial_lon_max",
        )
    ):
        # get bounds from raster tags
        bounds = (
            tags["geospatial_lon_min"],
            tags["geospatial_lat_min"],
            tags["geospatial_lon_max"],
            tags["geospatial_lat_max"],
        )
        logger.debug("Bounds from tags: {}", bounds)
        return bounds

    if ds.driver == "netCDF":
        bounds = calculate_netcdf_bounds(ds)
        logger.debug("Bounds calculated from netCDF lon/lat variables: {}", bounds)
        return bounds

    raise Exception("Unable to extract bounds from raster")


def calculate_netcdf_bounds(
    dataset: rasterio.DatasetReader
) -> tuple[float, float, float, float]:
    """
    Calculate the bounds of a netCDF dataset from the lon and lat variables.

    This is a slow operation as it requires to load all values in the lon and lat variables of the dataset.
    So it should only be used as a last resort.

    :param dataset: netCDF dataset
    :return: bounds as a tuple (left, bottom, right, top)
    """
    import numpy as np

    name_base = "netcdf:" + f'"{dataset.files[0]}"'
    name_lon = name_base + ":lon"
    name_lat = name_base + ":lat"
    with rasterio.open(name_lon) as ds_lon, rasterio.open(name_lat) as ds_lat:
        lon_arr = ds_lon.read(1)
        lon_min, lon_max = np.min(lon_arr).item(), np.max(lon_arr).item()
        lat_arr = ds_lat.read(1)
        lat_min, lat_max = np.min(lat_arr).item(), np.max(lat_arr).item()
    return lon_min, lat_min, lon_max, lat_max


def is_bounds_plausible(bounds: tuple[float, float, float, float]) -> bool:
    left, bottom, right, top = bounds
    if not -181 <= left <= right <= 181:
        return False
    if not -91 <= bottom <= top <= 91:
        return False

    return True


def get_processing_center(tags: dict) -> str | None:
    """
    Get the processing center information from the raster or vector metadata.

    :param tags: metadata tags
    :return: processing center, if available
    """
    processing_center = tags.get("institution") or tags.get("processing_centre")
    if processing_center is not None:
        processing_center = re.sub(
            r" (NV|GMBH)", "", processing_center, flags=re.IGNORECASE
        )
        processing_center = re.sub(
            r"LEGOS, CLS, CNES", "CLS", processing_center, flags=re.IGNORECASE
        )
        # capitalize known processing centers
        processing_center = re.sub(
            r"(VITO|CLS|EODC|FMI|IPMA)",
            lambda m: m.group(1).upper(),
            processing_center,
            flags=re.IGNORECASE,
        )

    processing_center = ",".join(pc.strip() for pc in processing_center.split(","))

    return processing_center
