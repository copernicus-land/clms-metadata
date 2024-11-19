from pathlib import Path

import rasterio
import rasterio.warp
import rioxarray
import shapely.geometry
from cloudpathlib import CloudPath
from loguru import logger
from overrides import overrides

from clms_metadata.models import ContentDate, Metadata, StringAttribute
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
                        bounds = rasterio.warp.transform_bounds(
                            sub_data.crs, "EPSG:4326", *sub_data.bounds
                        )
                else:
                    bounds = rasterio.warp.transform_bounds(
                        data.crs, "EPSG:4326", *data.bounds
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
                    name="processingCenter",
                    value_type=StringAttribute,
                    factory=lambda: self.get_processing_center(tags),
                )
                metadata.add_attribute(
                    name="title",
                    value_type=StringAttribute,
                    factory=lambda: tags.get("title"),
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
