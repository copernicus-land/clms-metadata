import os
from pathlib import Path
from typing import Optional

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
    endpoint: AnyUrl = Field(
        default_factory=lambda: AnyUrl(os.getenv("AWS_ENDPOINT_URL"))
    )
    aws_access_key_id: SecretStr = Field(
        default=SecretStr(os.getenv("AWS_ACCESS_KEY_ID"))
    )
    aws_secret_access_key: SecretStr = Field(
        default=SecretStr(os.getenv("AWS_SECRET_ACCESS_KEY"))
    )


class GeometrySettings(BaseModel):
    precision: float = 0.0000001
    """Precision grid size"""


class MetadataSettings(BaseModel):
    attributes: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class LinkSettings(BaseModel):
    template: str = "{product_type}/{dataset_name}/{content_date.start.year:04d}/{content_date.start.year:04d}{content_date.start.month:02}{content_date.start.day:02d}/{name}"
    rewrite: bool = False
    value: str | None = None


class Settings(BaseSettings):
    elasticsearch: Optional[ElasticsearchSettings] = None
    s3: Optional[S3Settings] = Field(
        default_factory=lambda: S3Settings()
        if any(
            env_var in os.environ
            for env_var in (
                "AWS_ENDPOINT_URL",
                "AWS_ACCESS_KEY_ID",
                "AWS_SECRET_ACCESS_KEY",
            )
        )
        else None
    )
    sources: list[MetadataSourceStr] = Field(
        default_factory=lambda: ["Path", "File", "Settings", "Lookup"]
    )
    metadata: Optional[MetadataSettings] = None
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
