import abc
import json
from abc import abstractmethod
from pathlib import Path

import jinja2
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.models import Metadata


class Writer(abc.ABC):
    """
    The Writer handles writing metadata in a template to a destination.
    """

    def __init__(self, template: str, settings: Settings):
        self.settings = settings
        self.env = jinja2.Environment(
            loader=jinja2.PackageLoader("clms_metadata", "resources/templates"),
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.policies["json.dumps_kwargs"] = {"sort_keys": False}
        self.template = self.env.get_template(template)

    def write(self, metadata: Metadata):
        """
        Write the metadata to the output.

        :param metadata:
        :return:
        """
        rendered = self.render(metadata)
        self._handle_write(metadata.name, rendered)

    @abstractmethod
    def _handle_write(self, name: str, rendered: str):
        pass

    def render(self, metadata: Metadata):
        """
        Render the metadata in the template.

        :param metadata: metadata object
        :return: rendered string
        """
        rendered = self.template.render(metadata=metadata.model_dump(mode="json"))
        return rendered


class LinesWriter(Writer):
    """
    Write output as JSON lines.
    """

    def _handle_write(self, name: str, rendered: str):
        print(json.dumps(json.loads(rendered)))


class FileWriter(Writer):
    """
    Write output as JSON files.
    """

    def __init__(self, output: Path, template: str, settings: Settings):
        super().__init__(template, settings)
        self.output = output
        self.output.mkdir(exist_ok=True, parents=True)

    def _handle_write(self, name: str, rendered: str):
        path = self.output / f"{name}.json"
        logger.info("Writing to file {}", path)
        with open(path, "w") as f:
            f.write(rendered)
