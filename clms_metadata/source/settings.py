from pathlib import Path

from cloudpathlib import CloudPath
from overrides import overrides

from clms_metadata.models.metadata import IntegerAttribute, Metadata, StringAttribute
from clms_metadata.source.base import MetadataSource


class SettingsSource(MetadataSource):
    """Retrieve static metadata from the settings."""

    @overrides
    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        super().get_info(product_files, metadata)
        if self.settings.metadata is None:
            return metadata

        if self.settings.metadata.model_extra:
            for name, value in self.settings.metadata.model_extra.items():
                setattr(metadata, name, value)

        for name, value in self.settings.metadata.attributes.items():
            value_type = IntegerAttribute if isinstance(value, int) else StringAttribute
            metadata.add_attribute(
                name=name, value_type=value_type, factory=lambda: value
            )

        return metadata
