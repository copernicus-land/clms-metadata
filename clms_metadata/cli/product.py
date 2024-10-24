import json
import re
from pathlib import Path

import cyclopts
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.storage import S3, LocalFileSystem, Storage

app = cyclopts.App()


@app.command()
def group_files(path: str, product_regex: str, config: Path | None = None) -> None:
    """
    Group the files into separate products based on the capturing groups specified in the product regex.

    :param path: path glob for products
    :param product_regex: product regex used to group files, must contain groups
    :param config: path to config file
    :return: list of grouped file paths
    """
    settings = Settings.from_yaml(config) if config else Settings()
    storage: Storage = S3(settings) if path.startswith("s3://") else LocalFileSystem()
    product_regex = re.compile(product_regex)
    files = list()
    for directory in storage.glob(path):
        logger.info("Looking for files in {}", directory)
        tmp_files = dict()
        for p in directory.rglob("*"):
            if match := product_regex.match(p.stem):
                key = match.groups()
                if key not in tmp_files:
                    tmp_files[key] = []
                tmp_files[key].append(p)
        files.extend(tmp_files.values())
    print(json.dumps(list(map(lambda fs: [str(f) for f in fs], files)), indent=2))
