import re

from loguru import logger
from pydantic import BaseModel, ConfigDict

from clms_metadata.models.metadata import Metadata


class Dataset(BaseModel):
    name: str
    templates: dict[str, str] = {}

    model_config = ConfigDict(extra="allow")


class ProductType(BaseModel):
    productType: str
    datasets: list[Dataset]
    templates: dict[str, str] = {}

    model_config = ConfigDict(extra="allow")


class Component(BaseModel):
    component: str
    productTypes: list[ProductType]
    templates: dict[str, str] = {}

    model_config = ConfigDict(extra="allow")


class FileRegex(BaseModel):
    regex: str
    templates: dict[str, str] = {}

    model_config = ConfigDict(extra="allow")


class DatasetMapping(BaseModel):
    datasetMapping: list[Component]
    fileRegex: list[FileRegex]
    templates: dict[str, str] = {}

    model_config = ConfigDict(extra="allow")

    def match(self, metadata: Metadata) -> dict[str, str] | None:
        for component in self.datasetMapping:
            for product_type in component.productTypes:
                for dataset in product_type.datasets:
                    for fileRegex in self.fileRegex:
                        output = {
                            k: v
                            for model in (
                                self,
                                component,
                                product_type,
                                dataset,
                                fileRegex,
                            )
                            for k, v in (
                                dict(model) | (model.model_extra or {})
                            ).items()
                            if isinstance(v, (str, int, float))
                        }
                        templates = (
                            self.templates
                            | component.templates
                            | product_type.templates
                            | dataset.templates
                            | fileRegex.templates
                        )
                        regex = re.compile(fileRegex.regex.format_map(output))
                        if m := regex.match(metadata.name):
                            logger.debug(
                                "Found matching dataset {} for {}",
                                dataset.name,
                                metadata.name,
                            )
                            output.update(m.groupdict())

                            format_map = output | {
                                a.name: a.value for a in metadata.attributes
                            }

                            for key, template in templates.items():
                                output[key] = template.format_map(format_map)

                            return output
        return None
