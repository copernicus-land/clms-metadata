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


def assert_dict_subset(d1, d2):
    """
    Assert that d1 is a subset of d2.

    :param d1:
    :param d2:
    :return:
    """
    if isinstance(d1, list):
        for i, _v in enumerate(d1):
            assert_dict_subset(d1[i], d2[i])
    elif isinstance(d1, dict):
        for k in d1:
            assert k in d2
            assert_dict_subset(d1[k], d2[k])
    else:
        assert d1 == d2, f"Expected elements '{d1}' and '{d2}' to be equal"
