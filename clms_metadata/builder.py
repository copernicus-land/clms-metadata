from pathlib import Path

from cloudpathlib import CloudPath
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.models import Metadata
from clms_metadata.source import MetadataSource
from clms_metadata.storage import Storage


class MetadataBuilder:
    def __init__(self, storage: Storage, settings: Settings):
        self.settings: Settings = settings
        self.storage = storage
        self.sources = [
            MetadataSource[source](self.settings) for source in settings.sources
        ]

    def build(self, paths: tuple[Path | CloudPath, ...]) -> Metadata:
        logger.info("Building metadata for {}", paths)
        info = dict()
        for metadata_source in self.sources:
            info = metadata_source.get_info(paths, info)

        m = Metadata(
            path=paths[0],
            **info,
        )
        return m
