import hashlib
from pathlib import Path

import rioxarray
import shapely.geometry
from cloudpathlib import CloudPath
from loguru import logger

from clms_metadata.models import Checksum, ContentDate, StringAttribute
from clms_metadata.source.base import MetadataSource, add_missing, add_missing_attribute


class FileSource(MetadataSource):
    """Retrieve metadata from the file content."""

    def get_info(self, product_files: list[Path | CloudPath], info: dict) -> dict:
        if len(product_files) == 1 and isinstance(product_files[0], Path):
            add_missing(info, "checksum", lambda: self.checksum(product_files[0]))

        for path in product_files:
            if path.suffix.lower() in (".nc", ".tiff", ".tif"):
                info = self._get_info_raster(path, info)

        return info

    def checksum(self, file: Path) -> Checksum:
        if self.settings.checksum.algorithm == "MD5":
            logger.debug("Calculating MD5 checksum of {}", file)
            with open(file, "rb") as f:
                md5sum = hashlib.md5()
                while chunk := f.read(self.settings.checksum.chunk_size):
                    md5sum.update(chunk)
            return Checksum(value=md5sum.hexdigest(), algorithm=md5sum.name.upper())
        else:
            raise ValueError(
                f"Checksum algorithm {self.settings.checksum.algorithm} is not supported"
            )

    def _get_info_raster(self, path: Path, info: dict) -> dict:
        with rioxarray.open_rasterio(path) as data:
            logger.debug(data.attrs)
            add_missing(
                info,
                "content_date",
                lambda: ContentDate(
                    start=data.attrs["time_coverage_start"],
                    end=data.attrs["time_coverage_end"],
                ),
            )
            add_missing(
                info,
                "geometry",
                lambda: shapely.set_precision(
                    shapely.geometry.box(*data.rio.bounds()),
                    grid_size=self.settings.geometry.precision,
                ),
            )  # TODO: check if half-pixel shift is needed?
            add_missing_attribute(
                info,
                "processingCenter",
                lambda: data.attrs["institution"],
                value_type=StringAttribute,
            )
            add_missing_attribute(
                info,
                "datasetIdentifier",
                lambda: (
                    data.attrs.get("parent_identifier")
                    or data.attrs.get("processing_centre")
                )
                .replace(" NV", "")
                .replace(" GMBH", ""),
                value_type=StringAttribute,
            )
        return info
