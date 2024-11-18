import json
import re
from pathlib import Path

import cyclopts
from loguru import logger

from clms_metadata.config import Settings
from clms_metadata.source.path import get_common_name
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
    grouped_files = _group_files(path, product_regex, config)
    print({get_common_name([Path(file) for file in group]): group for group in grouped_files})

def _group_files(path: str, product_regex: str, config: Path | None = None) -> list[list[str]]:
    """
    Group the files into separate products based on the capturing groups specified in the product regex.
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
    return list(map(lambda fs: [str(f) for f in fs], files))

@app.command()
def get_product_group_id(product_path: str, product_regex: str, config: Path | None = None) -> None:
    """
    For any product path, print the common identifier for the group of files to which the product belongs.

    :param product_path: product path of which we want to find the group identifier
    :param product_regex: product regex used to group files, must contain groups
    :param config: path to config file
    :return: None, prints the group identifier to stdout
    """
    all_grouped_files = _group_files(str(Path(product_path).parent), product_regex, config)
    product_groups = [common_files for common_files in all_grouped_files if product_path in common_files]
    if len(product_groups) == 0:
        logger.error("Product not found in the grouped files")
        raise ValueError("Product not found in the grouped files")
    elif len(product_groups) > 1:
        logger.error("Product found in multiple groups")
        raise ValueError("Product found in multiple groups")
    else:
        print(get_common_name([Path(f) for f in product_groups[0]]))


group_files("/data/MTDA/Copernicus/Land/global/geotiff/fraction_absorbed_par/fapar_300m_v1_10daily/2014/20140110/", "c_gls_FAPAR300-[A-Z]*((?:-RT.|)_[0-9]*_GLOBE_[A-Z]*_V[0-9]*.[0-9]*.[0-9]*)")
