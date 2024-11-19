import abc
from abc import abstractmethod
from pathlib import Path

from autoregistry import Registry
from cloudpathlib import CloudPath

from clms_metadata.config import Settings
from clms_metadata.models import Metadata
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
    def get_info(
        self, product_files: list[Path | CloudPath], metadata: Metadata
    ) -> Metadata:
        """
        Extract metadata for the product.

        :param product_files: list of files belonging to the product
        :param metadata: information dictionary
        :return: updated information dictionary
        """
        pass
