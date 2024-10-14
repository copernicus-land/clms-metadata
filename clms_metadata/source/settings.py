from pathlib import Path

from cloudpathlib import CloudPath

from clms_metadata.config import Settings
from clms_metadata.models import IntegerAttribute, StringAttribute
from clms_metadata.source.base import MetadataSource, add_missing_attribute


class SettingsSource(MetadataSource):
    """Retrieve static metadata from the settings."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def get_info(
        self, product_path: CloudPath, product_files: list[Path | CloudPath], info: dict
    ) -> dict:
        if self.settings.metadata is None:
            return info

        for name, value in self.settings.metadata["attributes"].items():
            value_type = IntegerAttribute if isinstance(value, int) else StringAttribute
            add_missing_attribute(
                info, name=name, factory=lambda: value, value_type=value_type
            )

        return info
