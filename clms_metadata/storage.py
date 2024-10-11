import abc
import glob
from typing import Iterator

from cloudpathlib import AnyPath
from loguru import logger

from clms_metadata.config import Settings


class Storage(abc.ABC):
    @abc.abstractmethod
    def glob(self, path: str) -> Iterator[AnyPath]:
        """
        Get the paths matching the provided glob pattern.

        :param path: glob path pattern
        :returns: iterator of paths
        """
        pass

    @staticmethod
    def list_files(path: AnyPath) -> Iterator[AnyPath]:
        """
        List all files in this subtree.

        :param path: path
        :return: iterator of all paths in this subtree
        """
        if path.is_file():
            yield path
        elif path.is_dir():
            for p in path.glob("**"):
                if p.is_file():
                    yield p

    @staticmethod
    def contains_glob(path: str) -> bool:
        return any(char in path for char in ["*", "?", "["])


class S3(Storage):
    def __init__(self, settings: Settings):
        from cloudpathlib import S3Client

        logger.debug("Initializing S3 client for endpoint {}", settings.s3.endpoint)
        self.s3_client = S3Client(
            endpoint_url=settings.s3.endpoint,
            aws_access_key_id=settings.s3.aws_access_key_id,
            aws_secret_access_key=settings.s3.aws_secret_access_key,
        )

    def glob(self, path: str) -> Iterator[str]:
        path, glob = self.build_path_glob(path)
        if glob is None:
            yield path
        else:
            logger.info("Searching {} with glob {}", path, glob)
            for p in path.glob(glob):
                yield p

    def build_path_glob(self, path: str) -> (AnyPath, str):
        glob_path = self.s3_client.CloudPath(path)
        logger.debug(glob_path.parts)
        path_list = list(glob_path.parents[::-1]) + [glob_path]
        for p in path_list:
            if glob.has_magic(p.name):
                concrete_path = p.parent
                glob_str = str(glob_path.relative_to(concrete_path))
                return concrete_path, glob_str
        return glob_path, None

    @staticmethod
    def split_bucket_key(path: str) -> (str, str):
        """
        Split a path or glob in a bucket and key.

        :param path: S3 path or glob
        :return: bucket and key
        """
        _, tmp = path.split("://", 1)
        bucket, key = tmp.split("/", 1)
        return bucket, key


class LocalFileSystem(Storage):
    def glob(self, path: str) -> Iterator[AnyPath]:
        yield from glob.iglob(path)
