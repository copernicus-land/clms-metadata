import difflib
import functools
import mimetypes
from pathlib import Path

from cloudpathlib import CloudPath
from loguru import logger
from overrides import overrides

from clms_metadata.source.base import MetadataSource, add_missing


class PathSource(MetadataSource):
    """Retrieve product metadata from the product path, e.g. filename."""

    @overrides
    def get_info(self, product_files: list[Path | CloudPath], info: dict) -> dict:
        if len(product_files) == 1:
            product_id = product_files[0].stem
        else:
            # try to find common string
            product_id = get_common_name(product_files)

        add_missing(info, "name", lambda: product_id)
        add_missing(info, "version", lambda: product_id.rsplit("_", 1)[1][:2].lower())
        add_missing(
            info,
            "content_type",
            lambda: mimetypes.guess_type(str(product_files[0]), strict=False)[0],
        )
        add_missing(info, "extension", lambda: product_files[0].suffix[1:].lower())
        add_missing(
            info, "origin_date", lambda: max(p.stat().st_mtime for p in product_files)
        )
        add_missing(
            info, "content_length", lambda: sum(p.stat().st_size for p in product_files)
        )

        return info


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
    while any(substr in common for substr in ("__", "--")):
        common = common.replace("__", "_")
        common = common.replace("--", "-")
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
                index = min(str_block.index(c) for c in ("_", "-"))
                str_block = str_block[index:]
            if i != len(blocks) - 1:
                # trim end of block to - or _
                index = max(str_block.rindex(c) for c in ("_", "-"))
                str_block = str_block[: index + 1]
            common += str_block
        except ValueError:
            # don't include the block if it cannot be trimmed to delimiting characters
            continue
    return common
