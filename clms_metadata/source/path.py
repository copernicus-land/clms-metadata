import mimetypes
from pathlib import Path

from cloudpathlib import CloudPath

from clms_metadata.source.base import MetadataSource, add_missing


class PathSource(MetadataSource):
    """Retrieve product metadata from the product path, e.g. filename."""

    def get_info(
        self,
        product_path: Path | CloudPath,
        product_files: list[Path | CloudPath],
        info: dict,
    ) -> dict:
        product_id = product_path.stem

        add_missing(info, "name", lambda: product_id)
        add_missing(
            info,
            "content_type",
            lambda: mimetypes.guess_type(str(product_files[0]), strict=False)[0],
        )
        add_missing(
            info, "origin_date", lambda: max(p.stat().st_mtime for p in product_files)
        )
        add_missing(
            info, "content_length", lambda: sum(p.stat().st_size for p in product_files)
        )

        return info
