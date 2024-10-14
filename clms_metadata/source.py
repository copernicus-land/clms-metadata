import abc
import mimetypes
from abc import abstractmethod
from pathlib import Path
from typing import Any, Type

from autoregistry import Registry
from cloudpathlib import CloudPath

from clms_metadata.config import Settings
from clms_metadata.models import (
    Attribute,
    ContentDate,
    IntegerAttribute,
    StringAttribute,
)


class MetadataSource(abc.ABC, Registry, suffix="Source"):
    @abstractmethod
    def __init__(self, settings: Settings):
        pass

    @abstractmethod
    def get_info(
        self,
        product_path: Path | CloudPath,
        product_files: list[Path | CloudPath],
        info: dict,
    ) -> dict:
        pass


class ElasticsearchSource(MetadataSource):
    def __init__(self, settings: Settings):
        from opensearchpy import OpenSearch

        self.client = OpenSearch(
            hosts=[
                {"host": host, "port": settings.elasticsearch.port}
                for host in settings.elasticsearch.hosts
            ],
        )
        self.index = settings.elasticsearch.index

    def get_info(
        self,
        product_path: Path | CloudPath,
        product_files: list[Path | CloudPath],
        info: dict,
    ) -> dict:
        _id = product_path.stem

        doc = self.client.get(index=self.index, id=_id)["_source"]
        if "name" not in info:
            info["name"] = doc["title"]

        if "geometry" not in info:
            info["geometry"] = doc["geometry"]

        if "origin_date" not in info:
            info["origin_date"] = doc["properties"]["processing_status"][
                "processing_end"
            ]

        if "content_date" not in info:
            info["content_date"] = ContentDate(
                start=doc["properties"]["beginposition"],
                end=doc["properties"]["endposition"],
            )

        if "tileid" in doc["properties"]:
            add_missing_attribute(
                info,
                name="tileId",
                value=doc["properties"]["tileid"],
                value_type=StringAttribute,
            )

        return info


class PathSource(MetadataSource):
    def __init__(self, settings: Settings):
        pass

    def get_info(
        self,
        product_path: Path | CloudPath,
        product_files: list[Path | CloudPath],
        info: dict,
    ) -> dict:
        product_id = product_path.stem

        if "name" not in info:
            info["name"] = product_id

        if "content_type" not in info:
            info["content_type"] = mimetypes.guess_type(
                str(product_files[0]), strict=False
            )[0]

        if "origin_date" not in info:
            info["origin_date"] = max(p.stat().st_mtime for p in product_files)

        if "content_length" not in info:
            info["content_length"] = sum(p.stat().st_size for p in product_files)

        return info


class FileSource(MetadataSource):
    def __init__(self, settings: Settings):
        pass

    def get_info(
        self, product_path: CloudPath, product_files: list[Path | CloudPath], info: dict
    ) -> dict:
        if "checksum" not in info:
            if len(product_files) == 1 and isinstance(product_files[0], Path):
                # TODO: calculate checksum of local file
                pass

        return info


class SettingsSource(MetadataSource):
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_info(
        self, product_path: CloudPath, product_files: list[Path | CloudPath], info: dict
    ) -> dict:
        if self.settings.metadata is None:
            return info

        for name, value in self.settings.metadata["attributes"].items():
            value_type = IntegerAttribute if isinstance(value, int) else StringAttribute
            add_missing_attribute(info, name=name, value=value, value_type=value_type)

        return info


def has_attribute(info: dict, attr_name: str) -> bool:
    attributes = info.get("attributes", [])
    return attr_name in (attr.name for attr in attributes)


def add_missing_attribute(
    info: dict, name: str, value: Any, value_type: Type[Attribute]
) -> dict:
    attributes = info.get("attributes", [])
    if not has_attribute(info, name):
        attributes.append(value_type(name=name, value=value))
        info["attributes"] = attributes
