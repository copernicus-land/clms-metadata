from pathlib import Path, PurePath

from cloudpathlib import AnyPath, CloudPath
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.constants import attributes
from clms_metadata.models.metadata import Metadata, PartialMetadata, StringAttribute
from clms_metadata.models.name_list import EOAssetNameList
from clms_metadata.source import MetadataSource
from clms_metadata.storage import Storage
from clms_metadata.util import unique_list


class MetadataBuilder:
    def __init__(self, storage: Storage, settings: Settings):
        self.settings: Settings = settings
        self.storage = storage
        self.eo_asset_name_list = _load_eo_asset_name_list(settings)
        self.sources = [
            MetadataSource[source](self.settings, self.storage, self.eo_asset_name_list)
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

        partial.path = self._get_link(paths, partial)
        partial = self.set_mission_info(partial)

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

    def set_mission_info(
        self,
        metadata: PartialMetadata,
    ) -> Metadata:
        """
        Set the mission, platform and instrument attributes on the metadata object.
        This method uses the information stored in the `missions` field of the metadata object.

        :param metadata: partial metadata object
        :return:
        """
        # add the mission/platform/instrument attributes
        mission_short_names = unique_list(
            msn if (msn := m.missionShortName) != self.settings.unspecified else None
            for m in metadata.missions
        )
        metadata.add_attribute(
            name=attributes.MISSION_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: ",".join(
                map(lambda v: v or self.settings.unspecified, mission_short_names)
            )
            or self.settings.unspecified,
            allow_none=True,
        )

        platform_short_names = unique_list(
            psn if (psn := p.platformShortName) != self.settings.unspecified else None
            for m in metadata.missions
            for p in m.platforms
        )
        metadata.add_attribute(
            name=attributes.PLATFORM_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: ",".join(
                map(lambda v: v or self.settings.unspecified, platform_short_names)
            )
            or self.settings.unspecified,
            allow_none=True,
        )

        platform_acronyms = unique_list(
            pa if (pa := p.platformAcronym) != self.settings.unspecified else None
            for m in metadata.missions
            for p in m.platforms
        )
        metadata.add_attribute(
            name=attributes.PLATFORM_ACRONYM,
            value_type=StringAttribute,
            factory=lambda: ",".join(
                map(lambda v: v or self.settings.unspecified, platform_acronyms)
            )
            or self.settings.unspecified,
            allow_none=True,
        )

        instrument_short_names = unique_list(
            isn if (isn := i.instrumentShortName) != self.settings.unspecified else None
            for m in metadata.missions
            for p in m.platforms
            for i in p.instruments
        )
        metadata.add_attribute(
            name=attributes.INSTRUMENT_SHORT_NAME,
            value_type=StringAttribute,
            factory=lambda: ",".join(
                map(lambda v: v or self.settings.unspecified, instrument_short_names)
            )
            or self.settings.unspecified,
            allow_none=True,
        )
        return metadata


def _load_eo_asset_name_list(settings: Settings) -> EOAssetNameList:
    if not settings.cache_dir.exists():
        logger.debug("Creating cache directory {}", settings.cache_dir)
        settings.cache_dir.mkdir(parents=True)

    local_path = (
        settings.cache_dir / PurePath(settings.eo_asset_name_list_url.path).name
    )
    if not local_path.exists():
        logger.info("Fetching EOAssetNameList from {}", settings.eo_asset_name_list_url)
        # fetch file from remote
        import urllib.request

        urllib.request.urlretrieve(
            url=str(settings.eo_asset_name_list_url), filename=local_path
        )

    return EOAssetNameList.from_yaml(local_path)
