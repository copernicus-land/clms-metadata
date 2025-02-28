import pytest

from clms_metadata.builder import _load_eo_asset_name_list
from clms_metadata.config import Settings
from clms_metadata.models.name_list import EOAssetNameList


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def eo_asset_name_list(settings: Settings) -> EOAssetNameList:
    return _load_eo_asset_name_list(settings)
