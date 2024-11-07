from pathlib import Path

import rioxarray
import shapely.geometry
from cloudpathlib import CloudPath
from loguru import logger

from clms_metadata.models import ContentDate, StringAttribute
from clms_metadata.source.base import MetadataSource, add_missing, add_missing_attribute


class FileSource(MetadataSource):
    """Retrieve metadata from the file content."""

    def get_info(self, product_files: list[Path | CloudPath], info: dict) -> dict:
        for path in product_files:
            if path.suffix.lower() in (".nc", ".tiff", ".tif"):
                info = self._get_info_raster(path, info)

        return info

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
                lambda: (
                    data.attrs.get("institution") or data.attrs.get("processing_centre")
                )
                .replace(" NV", "")
                .replace(" GMBH", ""),
                value_type=StringAttribute,
            )
        return info
