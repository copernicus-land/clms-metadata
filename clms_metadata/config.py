import os
from pathlib import Path
from typing import Optional

import platformdirs
import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic.networks import AnyUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

import clms_metadata
from clms_metadata.constants.attributes import UNSPECIFIED
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
        default_factory=lambda: SecretStr(os.getenv("AWS_ACCESS_KEY_ID"))
    )
    aws_secret_access_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("AWS_SECRET_ACCESS_KEY"))
    )
    no_sign_request: bool = Field(
        default_factory=lambda: os.getenv("AWS_NO_SIGN_REQUEST", False)
    )


class GeometrySettings(BaseModel):
    precision: float = 0.0000001
    """Precision grid size"""


class MetadataSettings(BaseModel):
    attributes: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class LinkSettings(BaseModel):
    template: str | None = None
    """For example: {product_type}/{content_date.start.year:04d}/{content_date.start.year:04d}{content_date.start.month:02}{content_date.start.day:02d}/{name}"""
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
        default_factory=lambda: [
            "Path",
            "File",
            "Settings",
            "Lookup",
        ]
    )
    metadata: Optional[MetadataSettings] = None
    geometry: GeometrySettings = GeometrySettings()
    link: LinkSettings = LinkSettings()

    vsicached: bool = False
    """Open raster files via the vsicached virtual filesystem"""

    unspecified: str | None = UNSPECIFIED
    """Placeholder value for unspecified attributes"""

    cache_dir: Path = platformdirs.user_cache_dir(
        appname=clms_metadata.__name__, version=clms_metadata.__version__
    )
    """Cache directory, defaults to user cache directory"""

    eo_asset_name_list_url: AnyUrl = "https://raw.githubusercontent.com/copernicus-land/EOAssets/1990be98767b60386b31bb273b50548cf3ecff1d/EOassetNameList.yaml"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        extra="ignore",
        env_parse_none_str="None",
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
