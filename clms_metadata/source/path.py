import datetime
import difflib
import functools
import re
from pathlib import Path

from cloudpathlib import CloudPath, S3Path
from loguru import logger
from overrides import overrides

from clms_metadata.constants import attributes, regex
from clms_metadata.constants.content_type import (
    CONTENT_TYPE_GEOJSON,
    CONTENT_TYPE_NETCDF,
    CONTENT_TYPE_TIFF,
)
from clms_metadata.constants.lookup_tables import (
    COG_EXTENSIONS,
    CONTENT_TYPE_TO_FILE_FORMAT,
)
from clms_metadata.models.metadata import (
    IntegerAttribute,
    Metadata,
    StringAttribute,
)
from clms_metadata.source.base import MetadataSource


class PathSource(MetadataSource):
    """Retrieve product metadata from the product path, e.g. filename."""

    @overrides
    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        super().get_info(product_files, metadata)
        if (
            len(product_files) == 1
            and get_content_type(product_files) != CONTENT_TYPE_TIFF
        ):
            product_id = product_files[0].stem
        else:
            # try to find common string
            product_id = get_common_name(product_files)

        if not metadata.name:
            metadata.name = product_id

        version = next(
            substr.lower()
            for substr in reversed(product_id.split("_"))
            if regex.VERSION.match(substr.lower())
        )
        metadata.add_attribute(  # full version
            name=attributes.PRODUCT_VERSION,
            value_type=StringAttribute,
            factory=lambda: version,
        )
        metadata.add_attribute(  # major version as int
            name=attributes.DATASET_VERSION,
            value_type=IntegerAttribute,
            factory=lambda: int(version[1:].split(".")[0]),
        )

        if not metadata.nominal_date:
            metadata.nominal_date = get_nominal_date(product_id)

        if not metadata.content_type:
            metadata.content_type = get_content_type(product_files)
        if not metadata.name_suffix:
            metadata.name_suffix = get_suffix(metadata.content_type)
        metadata.add_attribute(
            name=attributes.FILE_FORMAT,
            value_type=StringAttribute,
            factory=lambda: metadata.name_suffix,
        )
        if not metadata.origin_date:
            metadata.origin_date = max(get_mtime(p) for p in product_files)

        metadata.add_attribute(
            name=attributes.CONSOLIDATION_PERIOD,
            value_type=IntegerAttribute,
            factory=lambda: get_consolidation_period(product_id),
        )

        return metadata


def get_mtime(path: Path | CloudPath) -> float:
    """
    Get modification time of the file.

    :param path: file path
    :return: modification time as floating point since the epoch
    """
    if isinstance(path, S3Path):
        # try to read modification time from the object metadata: https://rclone.org/s3/#modification-times-and-hashes
        return (
            path.client._get_metadata(path)["extra"].get("mtime")
            or path.stat().st_mtime
        )
    else:
        return path.stat().st_mtime


def get_common_name(paths: list[Path | CloudPath]) -> str:
    """
    Given a list of files, get the common name for the product.
    File names segments are expected to be delimited by '-' or '_' characters.

    :param paths: list of paths belonging to the product
    :return: product name derived from the file names
    """
    values = set(map(lambda p: p.stem, paths))
    all_files_are_cog = all([p for p in paths if p.suffix in COG_EXTENSIONS])

    # Handle case of single file cogs with band in filename. (https://jira.vito.be/browse/GDD-3911)
    if len(values) == 1 and all_files_are_cog:
        [value] = values  # retrieve single item from set by unpacking
        if regex.LSP.match(value) or regex.SWI_STATIC.match(value):
            return value
        try:
            parts = value.split(
                "_"
            )  # decompose filename in parts to only try to replace in the relevant part
            parts[2] = re.sub(
                r"-[^-_]*(?=-|_|$)", "", parts[2], count=1
            )  # replace everything between the first occurrence of - and the next occurrence of either - or _
            values = {"_".join(parts)}
        except Exception as e:
            logger.exception(f"Unhandled cog filename pattern: {values}")
            raise e

    common = functools.reduce(_common_name_pair, values)
    # filter out duplicate consecutive hyphens or underscores
    while any(substr in common for substr in ("__", "--", "-_", "_-")):
        common = common.replace("__", "_")
        common = common.replace("--", "-")
        common = common.replace("-_", "_")
        common = common.replace("_-", "_")
    logger.debug("Reduced product identifier to {}", common)

    common = handle_anomalous_collections(name=common)

    return common


def _common_name_pair(a: str, b: str) -> str:
    matcher = difflib.SequenceMatcher(None, a, b)
    logger.debug("Searching for matching sequences {}, {}: {}", a, b, matcher.ratio())

    common = ""
    blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
    for i, block in enumerate(blocks):
        str_block = a[block.a : block.a + block.size]
        try:
            if i > 1:
                # trim start of block to - or _
                index = min([str_block.index(c) for c in ("_", "-") if c in str_block])
                str_block = str_block[index:]
            if i != len(blocks) - 1:
                # trim end of block to - or _
                index = max([str_block.rindex(c) for c in ("_", "-") if c in str_block])
                str_block = str_block[: index + 1]
            common += str_block
        except ValueError:
            # don't include the block if it cannot be trimmed to delimiting characters
            continue
    return common


def handle_anomalous_collections(name: str) -> str:
    """
    Some collections do not following conventions.
    These are handled outside the normal flow by taking the generated common name and correcting it.

    :param name: The common name created by the common logic
    :return: The corrected common name
    """
    if "LC100" in name:  # clms_global_lcc_100m_v3_yearly_geotiff
        return name.split(
            "-"
        )[
            0
        ]  # PROBAV_LC100_global_v3.0.1_2016-conso_EPSG-4326 -> PROBAV_LC100_global_v3.0.1_2016
    return name


def get_nominal_date(product_id: str) -> datetime.datetime:
    """
    Parse the date from the product ID.

    Nominal dates in filenames can take one of three forms:
        - YYYYMMDDhhmm (12 digits): the most common case
        - YEAR1----YEAR2 (4 digits, 4 hyphens, 4 digits) -> nominal date = Jan 1 of YEAR1:
            e.g. SWI static
        - YEAR1-YEAR2-MMDD (4 digits, hyphen, 4 digits, hyphen, 4 digits) -> nominal date = YEAR1/MM/DD:
            e.g. NDVI statistics
    """
    # remove c_gls or cgl from the start of the string
    trimmed_id = re.sub(r"^((c_gls)|cgl)_", "", product_id)
    date_part = trimmed_id.split("_")[1]
    if regex.DATETIME_DIGITS_MINUTES.fullmatch(date_part):
        date = datetime.datetime.strptime(date_part, "%Y%m%d%H%M")
    elif regex.DATETIME_DIGITS_SECONDS.fullmatch(date_part):
        date = datetime.datetime.strptime(date_part, "%Y%m%d%H%M%S")
    elif regex.DATE_YEAR1_YEAR2.fullmatch(date_part):
        date = datetime.datetime.strptime(date_part[0:4], "%Y")
    elif regex.DATE_YEAR1_YEAR2_MMDD.fullmatch(date_part):
        date = datetime.datetime.strptime(date_part[0:4] + date_part[-4:], "%Y%m%d")
    elif match := regex.LC100.fullmatch(product_id):
        date = datetime.datetime.strptime(match.group("year"), "%Y")
    else:
        raise ValueError(
            f"Product ID {product_id} did not match any of the expected nominal date formats"
        )
    return date.replace(tzinfo=datetime.timezone.utc)


def get_content_type(paths: list[Path | CloudPath]) -> str:
    suffixes = [p.suffix.lower() for p in paths]
    if ".nc" in suffixes:
        return CONTENT_TYPE_NETCDF
    elif any(s in suffixes for s in (".tif", ".tiff")):
        return CONTENT_TYPE_TIFF
    elif any(s in suffixes for s in (".geojson", ".json")):
        return CONTENT_TYPE_GEOJSON
    raise ValueError(f"Unsupported file types {suffixes}")


def get_suffix(content_type: str) -> str:
    return CONTENT_TYPE_TO_FILE_FORMAT[content_type]


def get_consolidation_period(product_id: str) -> str | None:
    if match := regex.CONSOLIDATION.search(product_id):
        return int(match.group(1))
    else:
        return None
