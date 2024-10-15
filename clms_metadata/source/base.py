import abc
from abc import abstractmethod
from pathlib import Path
from typing import Type

from autoregistry import Registry
from cloudpathlib import CloudPath

from clms_metadata.config import Settings
from clms_metadata.models import Attribute


class MetadataSource(abc.ABC, Registry, suffix="Source"):
    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def get_info(
        self,
        product_path: Path | CloudPath,
        product_files: list[Path | CloudPath],
        info: dict,
    ) -> dict:
        pass


def has_attribute(info: dict, attr_name: str) -> bool:
    attributes = info.get("attributes", [])
    return attr_name in (attr.name for attr in attributes)


def add_missing_attribute(
    info: dict, name: str, factory: callable, value_type: Type[Attribute]
) -> dict:
    attributes = info.get("attributes", [])
    if not has_attribute(info, name):
        attributes.append(value_type(name=name, value=factory()))
        info["attributes"] = attributes


def add_missing(
    info: dict,
    key: str,
    factory: callable,
) -> dict:
    """
    Add key-value pair to information dictionary in case the key is not present yet.
    The value is computed by executing the factory callable, in order to not run expensive operations when not needed.

    :param info: information dictionary
    :param key: key of the entry in the dictionary
    :param factory: factory to compute the value
    :return: the updated dictionary
    """
    if key not in info:
        info[key] = factory()

    return info
