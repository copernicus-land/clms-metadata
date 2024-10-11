from pathlib import Path

import cyclopts
from loguru import logger

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import Settings
from clms_metadata.writer import LinesWriter

app = cyclopts.App()


@app.command()
def create(
    path: str,
    output: Path,
    config: Path | None = None,
):
    settings = Settings.from_yaml(config) if config else Settings()
    logger.debug("Settings: {}", settings)
    builder = MetadataBuilder(glob=path, settings=settings)
    writer = LinesWriter(template="odata.json.jinja2", settings=settings)

    for m in builder.build():
        writer.write(m)
