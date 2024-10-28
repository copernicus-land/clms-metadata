from pathlib import Path

from cloudpathlib import CloudPath

from clms_metadata.config import Settings
from clms_metadata.models import ContentDate, StringAttribute
from clms_metadata.source.base import MetadataSource, add_missing, add_missing_attribute


class ElasticsearchSource(MetadataSource):
    """Retrieve product metadata from Elasticsearch."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        from opensearchpy import OpenSearch

        self.client = OpenSearch(
            hosts=[
                {"host": host, "port": settings.elasticsearch.port}
                for host in settings.elasticsearch.hosts
            ],
        )
        self.index = settings.elasticsearch.index

    def get_info(self, product_files: list[Path | CloudPath], info: dict) -> dict:
        _id = product_files[0].stem

        doc = self.client.get(index=self.index, id=_id)["_source"]

        add_missing(info, "name", lambda: doc["title"])
        add_missing(info, "geometry", lambda: doc["geometry"])
        add_missing(
            info,
            "origin_date",
            lambda: doc["properties"]["processing_status"]["processing_end"],
        )
        add_missing(
            info,
            "content_date",
            lambda: ContentDate(
                start=doc["properties"]["beginposition"],
                end=doc["properties"]["endposition"],
            ),
        )

        add_missing_attribute(
            info,
            name="tileId",
            factory=lambda: doc["properties"]["tileid"],
            value_type=StringAttribute,
        )

        return info
