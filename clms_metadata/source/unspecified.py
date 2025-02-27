from pathlib import Path

from cloudpathlib import CloudPath

from clms_metadata.constants import attributes
from clms_metadata.models.metadata import Metadata, StringAttribute
from clms_metadata.source import MetadataSource


class UnspecifiedSource(MetadataSource):
    """
    Source to add mandatory attributes with the configured 'unspecified' value if they do not exist already.
    """

    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        for attr_name in (
            attributes.MISSION_SHORT_NAME,
            attributes.PLATFORM_SHORT_NAME,
            attributes.PLATFORM_ACRONYM,
            attributes.INSTRUMENT_SHORT_NAME,
        ):
            if not metadata.has_attribute(attr_name):
                metadata.add_attribute(
                    name=attr_name,
                    value_type=StringAttribute,
                    factory=lambda: self.settings.unspecified,
                    allow_none=True,
                )

        return metadata
