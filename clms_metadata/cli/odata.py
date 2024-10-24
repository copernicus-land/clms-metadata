import json
import sys
from pathlib import Path

import cyclopts
from loguru import logger

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import Settings
from clms_metadata.writer import FileWriter, LinesWriter

app = cyclopts.App()


@app.command()
def create(
    path: str,
    output: Path | None = None,
    config: Path | None = None,
):
    settings = Settings.from_yaml(config) if config else Settings()
    logger.debug("Settings: {}", settings)
    builder = MetadataBuilder(glob=path, settings=settings)
    template = "odata.json.jinja2"
    writer = (
        FileWriter(output=output, template=template, settings=settings)
        if output is not None
        else LinesWriter(template=template, settings=settings)
    )

    for m in builder.build():
        writer.write(m)


@app.command()
def bulk_create(
    output: Path | None = None,
    config: Path | None = None,
):
    settings = Settings.from_yaml(config) if config else Settings()
    logger.debug("Settings: {}", settings)
    bulk_paths = json.load(sys.stdin)
    print(bulk_paths)
