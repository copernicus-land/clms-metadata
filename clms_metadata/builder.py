from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
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
        paths = [
            p
            for ps in map(lambda p: [p] if p.is_file() else p.rglob("*"), paths)
            for p in ps
        ]
        logger.debug("Expanded paths to {}", paths)
        info = dict()
        for metadata_source in self.sources:
            info = metadata_source.get_info(paths, info)

        # TODO: suffix name with format (eg. _nc or _tiff)
        info["name"] = f"{info['name']}_{info['extension']}"
        m = Metadata(
            path=self._get_link(info),
            **info,
        )
        return m

    def _get_link(self, info: dict) -> Path | CloudPath:
        link = AnyPath(self.settings.link.base) if self.settings.link.base else Path()
        link = link / self.settings.link.template.format_map(info)
        return link
