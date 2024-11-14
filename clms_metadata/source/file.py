from pathlib import Path

import rioxarray
import shapely.geometry
from cloudpathlib import CloudPath
from loguru import logger
from overrides import overrides

from clms_metadata.models import ContentDate, StringAttribute
from clms_metadata.source.base import MetadataSource, add_missing, add_missing_attribute


class FileSource(MetadataSource):
    """Retrieve metadata from the file content."""

    @overrides
    def get_info(self, product_files: list[Path | CloudPath], info: dict) -> dict:
        for path in product_files:
            if path.suffix.lower() in (".nc", ".tiff", ".tif"):
                info = self._get_info_raster(path, info)

        return info

    def _get_info_raster(self, path: Path | CloudPath, info: dict) -> dict:
        with self.storage.rasterio_env():
            with rioxarray.open_rasterio(str(path)) as data:
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
                    lambda: self.get_processing_center(data),
                    value_type=StringAttribute,
                )
        return info

    def get_processing_center(self, data) -> str | None:
        processing_center = data.attrs.get("institution") or data.attrs.get(
            "processing_centre"
        )
        if processing_center is not None:
            processing_center = processing_center.replace(" NV", "").replace(
                " GMBH", ""
            )
        return processing_center
