import os
from pathlib import Path
from typing import Any, Optional

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


class Settings(BaseSettings):
    elasticsearch: Optional[ElasticsearchSettings] = None
    s3: Optional[S3Settings] = None
    sources: list[MetadataSourceStr] = ["Path", "File", "Settings"]
    metadata: Optional[dict[str, Any]] = None

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        extra="ignore",
    )

    @classmethod
    def from_yaml(cls, path: Path):
        import yaml

        with open(path, "r") as f:
            conf = yaml.safe_load(f)
        return cls.model_validate(conf)
