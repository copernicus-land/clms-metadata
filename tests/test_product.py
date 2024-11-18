from pathlib import Path

import pytest

from clms_metadata.cli.product import get_product_group_id
from clms_metadata.source.path import get_common_name

fapar300_regex = "c_gls_FAPAR300-[A-Z]*((?:-RT.|)_[0-9]*_GLOBE_[A-Z]*_V[0-9]*.[0-9]*.[0-9]*)"
fapar300_path = "/data/MTDA/Copernicus/Land/global/geotiff/fraction_absorbed_par/fapar_300m_v1_10daily/2014/20140110/c_gls_FAPAR300-FAPAR_201401100000_GLOBE_PROBAV_V1.0.1.tiff"
fapar300_product_id = "c_gls_FAPAR300_201401100000_GLOBE_PROBAV_V1.0.1"

def test_cli():
    pass

def test_get_product_group_id():
    # assert fapar300_product_id == get_product_group_id(fapar300_path, fapar300_regex)
    pass

@pytest.mark.parametrize("names,common_name",
                         [([Path('/test/c_gls_FAPAR300-RMSE_201401100000_GLOBE_PROBAV_V1.0.1.tiff'),
                                Path('/test/c_gls_FAPAR300-FAPAR_201401100000_GLOBE_PROBAV_V1.0.1.tiff')],
                           'c_gls_FAPAR300_201401100000_GLOBE_PROBAV_V1.0.1'),]
                         )
def test_common_name(names, common_name):
    assert common_name == get_common_name(names)