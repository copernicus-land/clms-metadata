import re
from pathlib import Path

from cloudpathlib import AnyPath, CloudPath
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.models import IntegerAttribute, Metadata, PartialMetadata
from clms_metadata.source import MetadataSource
from clms_metadata.storage import Storage


class MetadataBuilder:
    def __init__(self, storage: Storage, settings: Settings):
        self.settings: Settings = settings
        self.storage = storage
        self.sources = [
            MetadataSource[source](self.settings, self.storage)
            for source in settings.sources
        ]

    def build(self, paths: tuple[Path | CloudPath, ...]) -> Metadata:
        """
        Build a Metadata object for the product.

        :param paths: file paths belonging to the product
        :return: Metadata object
        """
        logger.info("Building metadata for {}", paths)
        assert all(p.exists() for p in paths), "Provided path does not exist exist"
        expanded_paths = [
            p
            for ps in map(lambda p: [p] if p.is_file() else p.rglob("*"), paths)
            for p in ps
        ]
        logger.debug("Expanded paths to {}", expanded_paths)
        partial = PartialMetadata()

        for metadata_source in self.sources:
            partial = metadata_source.get_info(
                product_files=expanded_paths, metadata=partial
            )

        partial.add_attribute(
            "resolution", IntegerAttribute, lambda: get_resolution(partial.dataset_name)
        )
        partial.path = self._get_link(paths, partial)

        m = Metadata.model_validate(partial.model_dump())
        return m

    def _get_link(
        self, paths: tuple[Path | CloudPath, ...], metadata: Metadata
    ) -> Path | CloudPath:
        """
        Get the link of the product.
        The following options are considered (in order):
         - link value provided in settings
         - link rewrite following template in settings
         - original file path

        :param paths: product file paths
        :param metadata: metadata object
        :return: product path
        """
        if self.settings.link.value:
            return AnyPath(self.settings.link.value)
        elif self.settings.link.rewrite:
            return AnyPath(self.settings.link.template.format_map(metadata.__dict__))
        else:
            assert (
                len(paths) == 1
            ), "Either expected link to be set as a value, rewrite template or as a single input path."
            return paths[0]


regex_resolution = re.compile(r"_([\d.]+)(m|km)_")


def get_resolution(dataset_name: str) -> int:
    """
    Derive the resolution from the dataset name.

    :param dataset_name: dataset name
    :return: nominal resolution
    """
    match = regex_resolution.search(dataset_name)
    factor = 1000 if match.group(2) == "km" else 1
    res_base = float(match.group(1))
    resolution = int(res_base * factor)
    return resolution
