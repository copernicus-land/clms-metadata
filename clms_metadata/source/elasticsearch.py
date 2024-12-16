from pathlib import Path

from cloudpathlib import CloudPath
from overrides import overrides

from clms_metadata.config import Settings
from clms_metadata.models import ContentDate, Metadata, StringAttribute
from clms_metadata.source.base import MetadataSource
from clms_metadata.storage import Storage


class ElasticsearchSource(MetadataSource):
    """Retrieve product metadata from Elasticsearch."""

    @overrides
    def __init__(self, settings: Settings, storage: Storage):
        super().__init__(settings, storage)
        from opensearchpy import OpenSearch

        self.client = OpenSearch(
            hosts=[
                {"host": host, "port": settings.elasticsearch.port}
                for host in settings.elasticsearch.hosts
            ],
        )
        self.index = settings.elasticsearch.index

    @overrides
    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        super().get_info(product_files, metadata)
        _id = product_files[0].stem

        doc = self.client.get(index=self.index, id=_id)["_source"]

        if not metadata.name:
            metadata.name = doc["title"]
        if not metadata.geometry:
            metadata.geometry = doc["geometry"]
        if not metadata.origin_date:
            metadata.origin_date = doc["properties"]["processing_status"][
                "processing_end"
            ]
        if not metadata.content_date:
            metadata.content_date = ContentDate(
                start=doc["properties"]["beginposition"],
                end=doc["properties"]["endposition"],
            )
        metadata.add_attribute(
            name="tileId",
            value_type=StringAttribute,
            factory=lambda: doc["properties"].get("tileid"),
        )

        return metadata
