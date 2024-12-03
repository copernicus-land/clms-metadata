import datetime
import difflib
import functools
import re
from pathlib import Path
from typing import Final

from cloudpathlib import CloudPath, S3Path
from loguru import logger
from overrides import overrides

from clms_metadata.models import DateTimeOffsetAttribute, Metadata, StringAttribute
from clms_metadata.source.base import MetadataSource

CONTENT_TYPE_NETCDF: Final[str] = "application/netcdf"
CONTENT_TYPE_TIFF: Final[str] = "application/tiff"
CONTENT_TYPE_GEOJSON: Final[str] = "application/geo+json"


class PathSource(MetadataSource):
    """Retrieve product metadata from the product path, e.g. filename."""

    @overrides
    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        if len(product_files) == 1:
            product_id = product_files[0].stem
        else:
            # try to find common string
            product_id = get_common_name(product_files)

        if not metadata.name:
            metadata.name = product_id

        version = product_id.rsplit("_", 1)[1].lower()
        if not metadata.version:
            metadata.version = version[:2]  # major version
            metadata.add_attribute(
                name="productVersion",
                value_type=StringAttribute,
                factory=lambda: version,
            )  # full version

        metadata.add_attribute(
            name="nominalDate",
            value_type=DateTimeOffsetAttribute,
            factory=lambda: get_nominal_date(product_id),
        )

        if not metadata.content_type:
            metadata.content_type = get_content_type(product_files)
        if not metadata.name_suffix:
            metadata.name_suffix = get_suffix(metadata.content_type)
        if not metadata.origin_date:
            metadata.origin_date = max(get_mtime(p) for p in product_files)

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

    common = functools.reduce(_common_name_pair, values)
    # filter out duplicate consecutive hyphens or underscores
    while any(substr in common for substr in ("__", "--", "-_", "_-")):
        common = common.replace("__", "_")
        common = common.replace("--", "-")
        common = common.replace("-_", "_")
        common = common.replace("_-", "_")
    logger.debug("Reduced product identifier to {}", common)
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
    date_part = product_id.split("_")[3]
    if re.match(r"\d{12}", date_part):
        date = datetime.datetime.strptime(date_part, "%Y%m%d%H%M")
    elif re.match(r"\d{4}----\d{4}", date_part):
        date = datetime.datetime.strptime(date_part[0:4], "%Y")
    elif re.match(r"\d{4}-\d{4}-\d{4}", date_part):
        date = datetime.datetime.strptime(date_part[0:4] + date_part[-4:], "%Y%m%d")
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
    elif ".geojson" in suffixes:
        return CONTENT_TYPE_GEOJSON
    raise ValueError(f"Unsupported file types {suffixes}")


def get_suffix(content_type: str) -> str:
    return {
        CONTENT_TYPE_TIFF: "cog",
        CONTENT_TYPE_NETCDF: "nc",
        CONTENT_TYPE_GEOJSON: "geojson",
    }[content_type]
