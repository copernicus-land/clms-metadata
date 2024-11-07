import json
import sys
from pathlib import Path

import cyclopts
from loguru import logger

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import Settings
from clms_metadata.storage import Storage
from clms_metadata.writer import FileWriter, LinesWriter

app = cyclopts.App()


@app.command()
def create(
    *paths: str,
    output: Path | None = None,
    config: Path | None = None,
):
    """
    Create OData metadata for the product consisting of the provided file paths.

    :param paths: enumeration of file paths belonging to the product
    :param output: output for the OData metadata, leave empty to write to stdout
    :param config: YAML config file
    :return:
    """
    settings = Settings.from_yaml(config)
    logger.debug("Settings: {}", settings)
    storage = Storage.from_path(paths[0], settings)
    builder = MetadataBuilder(storage, settings=settings)
    template = "odata.json.jinja2"
    writer = (
        FileWriter(output=output, template=template, settings=settings)
        if output is not None
        else LinesWriter(template=template, settings=settings)
    )

    m = builder.build(tuple(storage.parse_path(p) for p in paths))
    writer.write(m)


@app.command()
def bulk_create(
    output: Path | None = None,
    config: Path | None = None,
):
    settings = Settings.from_yaml(config)
    logger.debug("Settings: {}", settings)
    bulk_paths = json.load(sys.stdin)
    logger.info("Generating metadata for {} products", len(bulk_paths))

    storage = Storage.from_path(bulk_paths[0][0], settings)
    builder = MetadataBuilder(storage=storage, settings=settings)
    template = "odata.json.jinja2"
    writer = (
        FileWriter(output=output, template=template, settings=settings)
        if output is not None
        else LinesWriter(template=template, settings=settings)
    )

    for product_files in bulk_paths:
        m = builder.build(tuple(Storage.parse_path(p) for p in product_files))
        writer.write(m)
