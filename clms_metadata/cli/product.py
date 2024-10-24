import json
import re
from pathlib import Path

import cyclopts
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.storage import S3, LocalFileSystem, Storage

app = cyclopts.App()


@app.command()
def group_files(
    path: str, product_regex: str, config: Path | None = None
) -> list[list[Path]]:
    settings = Settings.from_yaml(config) if config else Settings()
    storage: Storage = S3(settings) if path.startswith("s3://") else LocalFileSystem()
    product_regex = re.compile(product_regex)
    files = dict()
    for directory in storage.glob(path):
        logger.info("Looking for files in {}", directory)
        for p in directory.rglob("*"):
            if match := product_regex.match(p.stem):
                key = match.groups()
                if key not in files:
                    files[key] = []
                files[key].append(p)
    print(
        json.dumps(list(map(lambda fs: [str(f) for f in fs], files.values())), indent=2)
    )
    return list(files.values())
