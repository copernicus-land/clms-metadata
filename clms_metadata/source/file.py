import json
import re
from pathlib import Path

import rasterio
import rioxarray
import shapely.geometry
from cloudpathlib import CloudPath
from loguru import logger
from overrides import overrides
from pyproj import CRS, Transformer

from clms_metadata.constants import attributes, lookup_tables, regex
from clms_metadata.models.metadata import (
    ContentDate,
    IntegerAttribute,
    Metadata,
    StringAttribute,
)
from clms_metadata.models.name_list import EOAssetNameList, Mission, Platform
from clms_metadata.source.base import MetadataSource
from clms_metadata.util import unique_list

EPSG_4326 = CRS.from_epsg(4326)


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
                    if "time_coverage_start" in tags and "time_coverage_end" in tags:
                        metadata.content_date = ContentDate(
                            start=tags["time_coverage_start"],
                            end=tags["time_coverage_end"],
                        )
                    elif "time_start" in tags and "time_end" in tags:
                        metadata.content_date = ContentDate(
                            start=tags["time_start"],
                            end=tags["time_end"],
                        )

                if "creation_time" in tags:
                    metadata.origin_date = tags["creation_time"]

                if not metadata.geometry:
                    geometry = get_raster_bounds(data, tags)
                    geometry = shapely.make_valid(geometry)
                    metadata.geometry = (
                        shapely.set_precision(
                            geometry,
                            grid_size=self.settings.geometry.precision,
                            mode="keep_collapsed",
                        )
                        or geometry
                    )
                metadata.add_attribute(
                    name=attributes.PROCESSING_CENTER,
                    value_type=StringAttribute,
                    factory=lambda: get_processing_center(tags),
                )
                metadata.missions = list(
                    parse_platform(
                        tags.get("platform"), self.eo_asset_name_list
                    ).values()
                )
                metadata.instruments.extend(
                    parse_sensor(tags.get("sensor"), self.eo_asset_name_list)
                )

                if not metadata.dataset_identifier and (
                    dataset_identifier := get_dataset_identifier_from_parent_identifier(
                        tags.get("parent_identifier")
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

        metadata.add_attribute(
            name=attributes.CELL_ID,
            value_type=StringAttribute,
            factory=lambda: properties["resource"],
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

        geometry = shapely.geometry.shape(content["geometry"])
        metadata.geometry = (
            shapely.set_precision(
                geometry,
                grid_size=self.settings.geometry.precision,
                mode="keep_collapsed",
            )
            or geometry
        )
        metadata.origin_date = properties["updated"]

        metadata.add_attribute(
            name=attributes.PROCESSING_CENTER,
            value_type=StringAttribute,
            factory=lambda: get_processing_center(properties),
        )

        metadata.missions = list(
            parse_platform(properties.get("platform"), self.eo_asset_name_list).values()
        )
        metadata.instruments.extend(
            parse_sensor(properties.get("sensor"), self.eo_asset_name_list)
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
) -> dict[str, Mission]:
    """
    Get the platform information from the 'platform' metadata string.
    Returns a dictionary of missionShortName to platformShortName.

    :param platformstr: platform metadata string
    :return: platform information
    """
    if platformstr is None:
        return dict()
    platformstr = platformstr.upper().strip()
    platformstr = re.sub(r"[-_]", "", platformstr)
    platformstr = re.sub(r"SUOMI[-_ ]NPP", "SUOMINPP", platformstr, flags=re.IGNORECASE)
    platformstr = re.sub(
        regex.SENTINEL_WITH_SPACE, lambda m: f"{m.group(1)}{m.group(2)}", platformstr
    )

    # support for platforms with LIE 250m with old name for TERRA/AQUA/NOAA-20
    # TERRA (EOS AM-1) => [TERRA]
    if (
        any(modis in platformstr for modis in ["AQUA", "TERRA", "NOAA20"])
        and " (" in platformstr
    ):
        platformstr = platformstr.split(" (")[0]

    # turn platformstr into a map of missionShortName to platformShortName
    missions: dict[str, Mission] = {
        name.strip(): Mission(missionShortName=name.strip())
        for name in platformstr.split(",")
    }

    # Support for "AND" between platform names or platform serials
    # e.g. "SENTINEL-3A AND SENTINEL-3B" or "SENTINEL 3 (A AND B)"
    if " AND " in platformstr:
        for mission_short_name in list(missions):
            if regex_match_part := regex.PLATFORM_SERIALS_AND.search(
                mission_short_name
            ):
                missions.pop(mission_short_name)
                (mission_short_name, _) = mission_short_name.split(" (")
                mission_short_name = mission_short_name.replace(" ", "")
                if mission_short_name not in missions:
                    missions[mission_short_name] = Mission(
                        missionShortName=mission_short_name
                    )
                missions[mission_short_name].platforms.extend(
                    Platform(
                        platformShortName=build_platform_short_name(
                            mission_short_name, serial
                        )
                    )
                    for serial in regex_match_part.groups()
                )
            elif " AND " in mission_short_name:
                missions.pop(mission_short_name)
                for m in mission_short_name.split(" AND "):
                    if m not in missions:
                        missions[m] = Mission(missionShortName=m)

    # Support for SSM/SWI multi-mission products with eg "METOP B+C"
    if "+" in platformstr:
        for mission_short_name in list(missions):
            if "+" in mission_short_name:
                missions.pop(mission_short_name)
                (mission_short_name, platform_serial) = mission_short_name.split(" ")
                split_serial = platform_serial.split("+")
                if mission_short_name not in missions:
                    missions[mission_short_name] = Mission(
                        missionShortName=mission_short_name
                    )
                missions[mission_short_name].platforms.extend(
                    Platform(
                        platformShortName=build_platform_short_name(
                            mission_short_name, serial
                        )
                    )
                    for serial in split_serial
                )

    # We covered the AND and + syntaxes, all remaining spaces are between platforms
    # with exception of "METOP X"
    for mission_short_name in list(missions):
        if match := regex.METOP.match(mission_short_name):
            missions.pop(mission_short_name)
            mission_short_name, serial = match.groups()
            if mission_short_name not in missions:
                missions[mission_short_name] = Mission(
                    missionShortName=mission_short_name
                )
            missions[mission_short_name].platforms.append(
                Platform(
                    platformShortName=build_platform_short_name(
                        mission_short_name, serial
                    )
                )
            )
        elif " " in mission_short_name:
            missions.pop(mission_short_name)
            for msn in mission_short_name.split(" "):
                if msn not in missions:
                    missions[msn] = Mission(missionShortName=msn)

    # refine missions into platforms
    for mission_short_name in list(missions):
        if match := regex.GOES.match(mission_short_name):
            missions.pop(mission_short_name)
            mission_short_name, suffix = match.groups()
            platform_names = [f"{mission_short_name}{suffix}"] if suffix else list()
            if mission_short_name not in missions:
                missions[mission_short_name] = Mission(
                    missionShortName=mission_short_name
                )
            missions[mission_short_name].platforms.extend(
                Platform(platformShortName=name) for name in platform_names
            )
        elif match := regex.MSG.match(mission_short_name):
            # rewrite MSG to METEOSAT
            missions.pop(mission_short_name)
            base, num = match.groups()
            num = int(num) + 7
            mission_short_name = f"METEOSAT{num}"
            if mission_short_name not in missions:
                missions[mission_short_name] = Mission(
                    missionShortName=mission_short_name
                )
            missions[mission_short_name].platforms.append(
                Platform(platformShortName=mission_short_name)
            )
        elif match := (
            regex.SENTINEL_NUM_SERIAL.match(mission_short_name)
            or regex.SENTINEL_SHORT_NUM_SERIAL.match(mission_short_name)
        ):
            missions.pop(mission_short_name)
            base, num, serial = match.groups()
            mission_short_name = f"SENTINEL{num}"
            if mission_short_name not in missions:
                missions[mission_short_name] = Mission(
                    missionShortName=mission_short_name
                )
            missions[mission_short_name].platforms.append(
                Platform(
                    platformShortName=build_platform_short_name(
                        mission_short_name, serial
                    )
                )
            )
        elif mission_short_name not in eo_asset_name_list.missionShortNames:
            missions.pop(mission_short_name)
            missions[None] = Mission()
            continue

    return missions


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


def get_dataset_identifier_from_parent_identifier(identifier: str | None) -> str | None:
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
        parent_identifier = identifier_parts[-1]
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


def get_raster_bounds(ds: rasterio.DatasetReader, tags: dict) -> shapely.Polygon:
    """
    Get the bounds of a raster dataset.


    A few options are considered to extract the bounds:
        * bounds reported by rasterio
        * bounds of a subdataset reported by rasterio
        * bounds constructed from the geospatial_lon/lat_min/max tags
        * calculating bounds from netCDF lon/lat variables

    :param ds: raster dataset
    :param tags: raster metadata tags
    :return: geometry as a (reprojected) box (left, bottom, right, top)
    """
    if ds.crs:
        # get bounds of the raster directly
        geo = shapely.geometry.box(*ds.bounds)
        transformer = Transformer.from_crs(ds.crs, EPSG_4326, always_xy=True)
        geo = shapely.transform(geo, transformer.transform, interleaved=False)
        logger.debug("Bounds from raster: {}", geo)
        if is_bounds_plausible(geo):
            return geo
        else:
            logger.warning("Bounds {} are not plausible", geo)
    if ds.transform != rasterio.transform.Affine.identity():
        logger.debug(
            "Ignoring (missing) CRS in dataset. Using bounds as-is, assuming EPSG:4326."
        )
        geo = shapely.geometry.box(*ds.bounds)
        logger.debug("Bounds from dataset: {}", geo)
        if is_bounds_plausible(geo):
            return geo
        else:
            logger.warning("Bounds {} are not plausible", geo)
    else:
        logger.debug("No CRS or transform in dataset {}", ds.name)

    if ds.subdatasets:
        # get bounds of a subdataset
        logger.debug("Opening subdataset {}", ds.subdatasets[0])
        with rasterio.open(ds.subdatasets[0]) as sub_ds:
            geo = get_raster_bounds(sub_ds, tags)
            if geo:
                return geo

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
        geo = shapely.geometry.box(
            tags["geospatial_lon_min"],
            tags["geospatial_lat_min"],
            tags["geospatial_lon_max"],
            tags["geospatial_lat_max"],
        )
        logger.debug("Bounds from tags: {}", geo)
        return geo

    if ds.driver == "netCDF":
        geo = shapely.geometry.box(*calculate_netcdf_bounds(ds))
        logger.debug("Bounds calculated from netCDF lon/lat variables: {}", geo)
        return geo

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


def is_bounds_plausible(geo: shapely.Polygon) -> bool:
    left, bottom, right, top = geo.bounds
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
    processing_center = (
        tags.get("institution") or tags.get("processing_centre") or tags.get("producer")
    )
    if processing_center is not None:
        processing_center = re.sub(
            r" (NV|GMBH|AG)", "", processing_center, flags=re.IGNORECASE
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
    elif (c := tags.get("copyright")) and (m := re.search(r"processed by (\w+)", c)):
        processing_center = m.group(1)

    return processing_center
