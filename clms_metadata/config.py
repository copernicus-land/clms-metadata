import os
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic.networks import AnyUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from clms_metadata.types import MetadataSourceStr


class ElasticsearchSettings(BaseModel):
    hosts: list[str]
    port: int
    index: str


class S3Settings(BaseModel):
    endpoint: AnyUrl = os.getenv("AWS_ENDPOINT_URL")
    aws_access_key_id: SecretStr = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: SecretStr = os.getenv("AWS_SECRET_ACCESS_KEY")


class ChecksumSettings(BaseModel):
    algorithm: Literal["MD5"] = "MD5"
    chunk_size: int = 8192


class GeometrySettings(BaseModel):
    precision: float = 0.0000001
    """Precision grid size"""


class MetadataSettings(BaseModel):
    attributes: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class LinkSettings(BaseModel):
    base: str | None = None
    template: str = "{product_type}/{dataset_name}/{content_date.start.year:04d}/{content_date.start.year:04d}{content_date.start.month:02}{content_date.start.day:02d}/{name}"


class Settings(BaseSettings):
    elasticsearch: Optional[ElasticsearchSettings] = None
    s3: Optional[S3Settings] = None
    sources: list[MetadataSourceStr] = ["Path", "File", "Settings"]
    metadata: Optional[MetadataSettings] = None
    checksum: ChecksumSettings = ChecksumSettings()
    geometry: GeometrySettings = GeometrySettings()
    link: LinkSettings = LinkSettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        extra="ignore",
    )

    @classmethod
    def from_yaml(cls, path: Path | None):
        """
        Read the config from a YAML file.

        :param path: path of the YAML file to read
        :return: Settings object
        """
        if path is None:
            return Settings()

        with open(path, "r") as f:
            conf = yaml.safe_load(f)
        return cls.model_validate(conf)
