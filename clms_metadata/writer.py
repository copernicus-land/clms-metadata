import abc
import json
from abc import abstractmethod

import jinja2

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
        self._handle_write(rendered)

    @abstractmethod
    def _handle_write(self, rendered: str):
        pass

    def render(self, metadata: Metadata):
        rendered = self.template.render(metadata=metadata.model_dump(exclude_none=True))
        return rendered


class LinesWriter(Writer):
    def _handle_write(self, rendered: str):
        print(json.dumps(json.loads(rendered)))
