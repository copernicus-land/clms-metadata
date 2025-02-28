from pathlib import Path

import cyclopts
from clms_metadata.config import Settings
from loguru import logger
import rich
from rich.tree import Tree
import shutil

app = cyclopts.App()
settings = Settings()


@app.command()
def cache(flush: bool = False):
    """
    Interact with the application cache directory.

    By default, the name and contents of the cache directory will be displayed.
    Optionally, it is possible to delete the cache.

    :param flush: delete the cache directory
    :return:
    """
    cache_dir = settings.cache_dir
    logger.info("Cache directory: {}", cache_dir)
    if not cache_dir.exists():
        logger.info("Cache directory does not exist yet")
        return

    tree = Tree(f":open_file_folder: [link file://{cache_dir}]{cache_dir}")
    _build_directory_tree(cache_dir, tree)
    rich.print(tree)

    if flush:
        logger.info("Deleting cache directory")
        shutil.rmtree(cache_dir)


def _build_directory_tree(path: Path, tree: Tree):
    paths = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for p in paths:
        if p.is_dir():
            branch = tree.add(
                f":open_file_folder: [link file://{p}]{p.name}"
            )
            _build_directory_tree(p, branch)
        else:
            tree.add(f":page_facing_up: [link file://{p}]{p.name}")
