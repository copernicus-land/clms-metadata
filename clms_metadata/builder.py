from pathlib import Path
from typing import Iterator

from cloudpathlib import CloudPath
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.models import Metadata
from clms_metadata.source import MetadataSource
from clms_metadata.storage import S3, LocalFileSystem, Storage


class MetadataBuilder:
    def __init__(self, glob: str, settings: Settings):
        self.glob = glob
        self.settings: Settings = settings
        self.storage: Storage = (
            S3(settings) if glob.startswith("s3://") else LocalFileSystem()
        )
        self.sources = [
            MetadataSource[source](self.settings) for source in settings.sources
        ]

    def build(self) -> Iterator[Metadata]:
        for path in self.storage.glob(self.glob):
            yield self._build_single(path)

    def _build_single(self, product_path: Path | CloudPath) -> Metadata:
        logger.info("Building metadata for {}", product_path)
        file_paths = list(self.storage.list_files(product_path))
        info = dict()
        for metadata_source in self.sources:
            info = metadata_source.get_info(product_path, file_paths, info)

        m = Metadata(
            path=product_path,
            **info,
        )
        return m
