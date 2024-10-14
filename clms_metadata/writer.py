import abc
import json
from abc import abstractmethod
from pathlib import Path

import jinja2
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.models import Metadata


class Writer(abc.ABC):
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
        rendered = self.render(metadata)
        self._handle_write(metadata.name, rendered)

    @abstractmethod
    def _handle_write(self, name: str, rendered: str):
        pass

    def render(self, metadata: Metadata):
        rendered = self.template.render(metadata=metadata.model_dump(exclude_none=True))
        return rendered


class LinesWriter(Writer):
    def _handle_write(self, name: str, rendered: str):
        print(json.dumps(json.loads(rendered)))


class FileWriter(Writer):
    def __init__(self, output: Path, template: str, settings: Settings):
        super().__init__(template, settings)
        self.output = output
        self.output.mkdir(exist_ok=True, parents=True)

    def _handle_write(self, name: str, rendered: str):
        path = self.output / f"{name}.json"
        logger.info("Writing to file {}", path)
        with open(path, "w") as f:
            f.write(rendered)
