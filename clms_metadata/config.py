import os
from pathlib import Path
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, SecretStr
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
    endpoint: str
    aws_access_key_id: SecretStr = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: SecretStr = os.getenv("AWS_SECRET_ACCESS_KEY")


class ChecksumSettings(BaseModel):
    algorithm: Literal["MD5"] = "MD5"
    chunk_size: int = 8192


class GeometrySettings(BaseModel):
    precision: float = 0.0000001
    """Precision grid size"""


class Settings(BaseSettings):
    elasticsearch: Optional[ElasticsearchSettings] = None
    s3: Optional[S3Settings] = None
    sources: list[MetadataSourceStr] = ["Path", "File", "Settings"]
    metadata: Optional[dict[str, Any]] = None
    checksum: ChecksumSettings = ChecksumSettings()
    geometry: GeometrySettings = GeometrySettings()

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
