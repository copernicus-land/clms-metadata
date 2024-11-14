import abc
from abc import abstractmethod
from pathlib import Path
from typing import Type

from autoregistry import Registry
from cloudpathlib import CloudPath

from clms_metadata.config import Settings
from clms_metadata.models import Attribute
from clms_metadata.storage import Storage


class MetadataSource(abc.ABC, Registry, suffix="Source"):
    """
    A metadata source provides information about a product.
    Different sources can be implemented to extract metadata in various ways.
    """

    def __init__(self, settings: Settings, storage: Storage):
        self.settings = settings
        self.storage = storage

    @abstractmethod
    def get_info(self, product_files: list[Path | CloudPath], info: dict) -> dict:
        """
        Extract metadata for the product.

        :param product_files: list of files belonging to the product
        :param info: information dictionary
        :return: updated information dictionary
        """
        pass


def has_attribute(info: dict, attr_name: str) -> bool:
    """
    Indicates whether the information dictionary already includes an attribute with the given name.
    :param info: information dictionary
    :param attr_name: attribute name
    :return: boolean indicating whether the attribute already exists
    """
    attributes = info.get("attributes", [])
    return attr_name in (attr.name for attr in attributes)


def add_missing_attribute(
    info: dict, name: str, factory: callable, value_type: Type[Attribute]
) -> dict:
    """
    Add an attribute to the given info dictionary if it is not present.

    :param info: information dictionary
    :param name: name of the attribute
    :param factory: factory method to extract the value
    :param value_type: value type
    :return: the updated dictionary
    """
    attributes = info.get("attributes", [])
    if not has_attribute(info, name):
        value = factory()
        if value is not None:
            attributes.append(value_type(name=name, value=value))
        info["attributes"] = attributes
    return info


def add_missing(
    info: dict,
    key: str,
    factory: callable,
) -> dict:
    """
    Add key-value pair to information dictionary in case the key is not present yet.
    The value is extracted by executing the factory callable, in order to not run expensive operations when not needed.

    :param info: information dictionary
    :param key: key of the entry in the dictionary
    :param factory: factory method to extract the value
    :return: the updated dictionary
    """
    if key not in info:
        info[key] = factory()

    return info
