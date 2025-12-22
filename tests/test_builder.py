from pathlib import Path

import pyjson5
import pytest

from clms_metadata.builder import MetadataBuilder
from clms_metadata.config import LinkSettings, Settings
from clms_metadata.models.metadata import Metadata
from clms_metadata.storage import LocalFileSystem

test_root = Path(__file__).parent
test_data = test_root / "data"
test_reference = test_root / "reference"


@pytest.mark.parametrize(
    ("files", "reference"),
    [
        # ndvi_global_1km_10daily_v3
        (
            (
                test_data
                / "vegetation_indices/ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi_global_1km_10daily_v3/c_gls_NDVI_202004010000_GLOBE_PROBAV_V3.0.1_nc.json5",
        ),
        (
            tuple(
                test_data
                / "vegetation_indices/ndvi_global_1km_10daily_v3"
                / f"c_gls_NDVI-{band}_199901010000_GLOBE_VGT_V3.0.1.tiff"
                for band in ("NDVI", "NOBS", "QFLAG", "TIMEGRID", "UNC")
            ),
            test_reference
            / "vegetation_indices/ndvi_global_1km_10daily_v3/c_gls_NDVI_199901010000_GLOBE_VGT_V3.0.1_cog.json5",
        ),
        # ba_global_300m_daily_v3
        (
            (
                test_data
                / "burnt_area/ba_global_300m_daily_v3/c_gls_BA300-NRT_202402200000_GLOBE_S3_V3.1.1.nc",
            ),
            test_reference
            / "burnt_area/ba_global_300m_daily_v3/c_gls_BA300-NRT_202402200000_GLOBE_S3_V3.1.1_nc.json5",
        ),
        # ba_global_300m_daily_v3
        (
            (
                test_data
                / "burnt_area/ba_global_300m_monthly_v3/c_gls_BA300-NTC_202306010000_GLOBE_S3_V3.1.1.nc",
            ),
            test_reference
            / "burnt_area/ba_global_300m_monthly_v3/c_gls_BA300-NTC_202306010000_GLOBE_S3_V3.1.1_nc.json5",
        ),
        # dmp_global_1km_10daily_v2/
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/dmp_global_1km_10daily_v2/c_gls_DMP_200109100000_GLOBE_VGT_V2.0.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/dmp_global_1km_10daily_v2/c_gls_DMP_200109100000_GLOBE_VGT_V2.0.1_nc.json5",
        ),
        # dmp_global_300m_10daily_v1
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/dmp_global_300m_10daily_v1/c_gls_DMP300-RT5_201502200000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/dmp_global_300m_10daily_v1/c_gls_DMP300-RT5_201502200000_GLOBE_PROBAV_V1.0.1_nc.json5",
        ),
        # gdmp_global_1km_10daily_v2
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/gdmp_global_1km_10daily_v2/c_gls_GDMP_199901310000_GLOBE_VGT_V2.0.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/gdmp_global_1km_10daily_v2/c_gls_GDMP_199901310000_GLOBE_VGT_V2.0.1_nc.json5",
        ),
        # gdmp_global_300m_10daily_v1
        (
            (
                test_data
                / "dry-gross_dry_matter_productivity/gdmp_global_300m_10daily_v1/c_gls_GDMP300-RT0_202501100000_GLOBE_OLCI_V1.1.1.nc",
            ),
            test_reference
            / "dry-gross_dry_matter_productivity/gdmp_global_300m_10daily_v1/c_gls_GDMP300-RT0_202501100000_GLOBE_OLCI_V1.1.1_nc.json5",
        ),
        # gpp_global_300m_10daily_v1
        (
            (
                test_data
                / "net-gross_primary_production/gpp_global_300m_10daily_v1/c_gls_GPP300-RT2_202410310000_GLOBE_OLCI_V1.1.1.nc",
            ),
            test_reference
            / "net-gross_primary_production/gpp_global_300m_10daily_v1/c_gls_GPP300-RT2_202410310000_GLOBE_OLCI_V1.1.1_nc.json5",
        ),
        # npp_global_300m_10daily_v1
        (
            (
                test_data
                / "net-gross_primary_production/npp_global_300m_10daily_v1/c_gls_NPP300-RT6_202307100000_GLOBE_OLCI_V1.1.1.nc",
            ),
            test_reference
            / "net-gross_primary_production/npp_global_300m_10daily_v1/c_gls_NPP300-RT6_202307100000_GLOBE_OLCI_V1.1.1_nc.json5",
        ),
        # fapar_global_1km_10daily_v2
        (
            (
                test_data
                / "vegetation_properties/fapar_global_1km_10daily_v2/c_gls_FAPAR_199908100000_GLOBE_VGT_V2.0.2.nc",
            ),
            test_reference
            / "vegetation_properties/fapar_global_1km_10daily_v2/c_gls_FAPAR_199908100000_GLOBE_VGT_V2.0.2_nc.json5",
        ),
        # fapar_global_300m_10daily_v1
        (
            (
                test_data
                / "vegetation_properties/fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2.nc",
            ),
            test_reference
            / "vegetation_properties/fapar_global_300m_10daily_v1/c_gls_FAPAR300-RT6_202302100000_GLOBE_OLCI_V1.1.2_nc.json5",
        ),
        # fcover_global_1km_10daily_v2
        (
            (
                test_data
                / "vegetation_properties/fcover_global_1km_10daily_v2/c_gls_FCOVER-RT2_201909100000_GLOBE_PROBAV_V2.0.1.nc",
            ),
            test_reference
            / "vegetation_properties/fcover_global_1km_10daily_v2/c_gls_FCOVER-RT2_201909100000_GLOBE_PROBAV_V2.0.1_nc.json5",
        ),
        # fcover_global_300m_10daily_v1
        (
            (
                test_data
                / "vegetation_properties/fcover_global_300m_10daily_v1/c_gls_FCOVER300_201503200000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "vegetation_properties/fcover_global_300m_10daily_v1/c_gls_FCOVER300_201503200000_GLOBE_PROBAV_V1.0.1_nc.json5",
        ),
        # lst_global_5km_hourly_v1
        (
            (
                test_data
                / "land_surface_temperature/lst_global_5km_hourly_v1/c_gls_LST_201409261600_GLOBE_GEO_V1.2.1.nc",
            ),
            test_reference
            / "land_surface_temperature/lst_global_5km_hourly_v1/c_gls_LST_201409261600_GLOBE_GEO_V1.2.1_nc.json5",
        ),
        # lst_global_5km_hourly_v2
        (
            (
                test_data
                / "land_surface_temperature/lst_global_5km_hourly_v2/c_gls_LST_202501121100_GLOBE_GEO_V2.1.2.nc",
            ),
            test_reference
            / "land_surface_temperature/lst_global_5km_hourly_v2/c_gls_LST_202501121100_GLOBE_GEO_V2.1.2_nc.json5",
        ),
        # lst_global_3km_hourly_v3
        (
            (
                test_data
                / "land_surface_temperature/lst_global_3km_hourly_v3/c_gls_LST_202408011200_GLOBE_GEO_V3.0.1.nc",
            ),
            test_reference
            / "land_surface_temperature/lst_global_3km_hourly_v3/c_gls_LST_202408011200_GLOBE_GEO_V3.0.1_nc.json5",
        ),
        # lst-daily-cycle_global_5km_10daily_v1
        (
            (
                test_data
                / "land_surface_temperature/lst-daily-cycle_global_5km_10daily_v1/nc/c_gls_LST10-DC_201909010000_GLOBE_GEO_V1.2.1.nc",
            ),
            test_reference
            / "land_surface_temperature/lst-daily-cycle_global_5km_10daily_v1/c_gls_LST10-DC_201909010000_GLOBE_GEO_V1.2.1_nc.json5",
        ),
        (
            (
                test_data
                / "land_surface_temperature/lst-daily-cycle_global_5km_10daily_v1/cog/",
            ),
            test_reference
            / "land_surface_temperature/lst-daily-cycle_global_5km_10daily_v1/c_gls_LST10-DC_201701110000_GLOBE_GEO_V1.2.1_cog.json5",
        ),
        # lst-daily-cycle_global_5km_10daily_v2
        (
            (
                test_data
                / "land_surface_temperature/lst-daily-cycle_global_5km_10daily_v2/c_gls_LST10-DC_202305210000_GLOBE_GEO_V2.1.1.nc",
            ),
            test_reference
            / "land_surface_temperature/lst-daily-cycle_global_5km_10daily_v2/c_gls_LST10-DC_202305210000_GLOBE_GEO_V2.1.1_nc.json5",
        ),
        # lst-tci_global_5km_10daily_v1
        (
            (
                test_data
                / "land_surface_temperature/lst-tci_global_5km_10daily_v1/c_gls_LST10-TCI_202002210000_GLOBE_GEO_V1.2.1.nc",
            ),
            test_reference
            / "land_surface_temperature/lst-tci_global_5km_10daily_v1/c_gls_LST10-TCI_202002210000_GLOBE_GEO_V1.2.1_nc.json5",
        ),
        # lst-tci_global_5km_10daily_v2
        (
            (
                test_data
                / "land_surface_temperature/lst-tci_global_5km_10daily_v2/c_gls_LST10-TCI_202101110000_GLOBE_GEO_V2.1.1.nc",
            ),
            test_reference
            / "land_surface_temperature/lst-tci_global_5km_10daily_v2/c_gls_LST10-TCI_202101110000_GLOBE_GEO_V2.1.1_nc.json5",
        ),
        # lai_global_1km_10daily_v2
        (
            (
                test_data
                / "vegetation_properties/lai_global_1km_10daily_v2/c_gls_LAI_200804200000_GLOBE_VGT_V2.0.1.nc",
            ),
            test_reference
            / "vegetation_properties/lai_global_1km_10daily_v2/c_gls_LAI_200804200000_GLOBE_VGT_V2.0.1_nc.json5",
        ),
        # lai_global_300m_10daily_v1
        (
            (
                test_data
                / "vegetation_properties/lai_global_300m_10daily_v1/c_gls_LAI300_201402200000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "vegetation_properties/lai_global_300m_10daily_v1/c_gls_LAI300_201402200000_GLOBE_PROBAV_V1.0.1_nc.json5",
        ),
        # ndvi_global_1km_10daily_v2
        (
            (
                test_data
                / "vegetation_indices/ndvi_global_1km_10daily_v2/c_gls_NDVI_200112210000_GLOBE_VGT_V2.2.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi_global_1km_10daily_v2/c_gls_NDVI_200112210000_GLOBE_VGT_V2.2.1_nc.json5",
        ),
        # ndvi_global_300m_10daily_v1
        (
            (
                test_data
                / "vegetation_indices/ndvi_global_300m_10daily_v1/c_gls_NDVI300_201706010000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi_global_300m_10daily_v1/c_gls_NDVI300_201706010000_GLOBE_PROBAV_V1.0.1_nc.json5",
        ),
        # ndvi_global_300m_10daily_v2
        (
            (
                test_data
                / "vegetation_indices/ndvi_global_300m_10daily_v2/c_gls_NDVI300_202101210000_GLOBE_OLCI_V2.0.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi_global_300m_10daily_v2/c_gls_NDVI300_202101210000_GLOBE_OLCI_V2.0.1_nc.json5",
        ),
        # ndvi-sts_global_1km_10daily_v3
        (
            (
                test_data
                / "vegetation_indices/ndvi-sts_global_1km_10daily_v3/c_gls_NDVI-STS_2015-2019-1211_GLOBE_PROBAV_V3.0.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi-sts_global_1km_10daily_v3/c_gls_NDVI-STS_2015-2019-1211_GLOBE_PROBAV_V3.0.1_nc.json5",
        ),
        # ndvi-lts_global_1km_10daily_v3
        (
            (
                test_data
                / "vegetation_indices/ndvi-lts_global_1km_10daily_v3/c_gls_NDVI-LTS_1999-2019-0511_GLOBE_VGT-PROBAV_V3.0.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi-lts_global_1km_10daily_v3/c_gls_NDVI-LTS_1999-2019-0511_GLOBE_VGT-PROBAV_V3.0.1_nc.json5",
        ),
        # ndvi-lts_global_1km_10daily_v2
        (
            (
                test_data
                / "vegetation_indices/ndvi-lts_global_1km_10daily_v2/c_gls_NDVI-LTS_1999-2017-1001_GLOBE_VGT-PROBAV_V2.2.1.nc",
            ),
            test_reference
            / "vegetation_indices/ndvi-lts_global_1km_10daily_v2/c_gls_NDVI-LTS_1999-2017-1001_GLOBE_VGT-PROBAV_V2.2.1_nc.json5",
        ),
        # swi_europe_1km_daily_v1
        (
            (
                test_data
                / "soil_water_index/swi_europe_1km_daily_v1/c_gls_SWI1km_201608131200_CEURO_SCATSAR_V1.0.1.nc",
            ),
            test_reference
            / "soil_water_index/swi_europe_1km_daily_v1/c_gls_SWI1km_201608131200_CEURO_SCATSAR_V1.0.1_nc.json5",
        ),
        # swi_global_12.5km_10daily_v3
        (
            (
                test_data
                / "soil_water_index/swi_global_12.5km_10daily_v3/c_gls_SWI10_201206211200_GLOBE_ASCAT_V3.1.1.nc",
            ),
            test_reference
            / "soil_water_index/swi_global_12.5km_10daily_v3/c_gls_SWI10_201206211200_GLOBE_ASCAT_V3.1.1_nc.json5",
        ),
        # swi_global_12.5km_daily_v3
        (
            (
                test_data
                / "soil_water_index/swi_global_12.5km_daily_v3/c_gls_SWI_202302141200_GLOBE_ASCAT_V3.2.1.nc",
            ),
            test_reference
            / "soil_water_index/swi_global_12.5km_daily_v3/c_gls_SWI_202302141200_GLOBE_ASCAT_V3.2.1_nc.json5",
        ),
        # swi-timeseries_global_12.5km_daily_v3
        (
            (
                test_data
                / "soil_water_index/swi-timeseries_global_12.5km_daily_v3/c_gls_SWI-TS_202312310000_C0348_ASCAT_V3.2.1.nc",
            ),
            test_reference
            / "soil_water_index/swi-timeseries_global_12.5km_daily_v3/c_gls_SWI-TS_202312310000_C0348_ASCAT_V3.2.1_nc.json5",
        ),
        # swi-static_global_12.5km_daily_v3
        (
            (
                test_data
                / "soil_water_index/swi-static_global_12.5km_daily_v3/c_gls_SWI-STATIC-CI_2007----2017_GLOBE_SWI-GLDAS_V1.1.1.nc",
            ),
            test_reference
            / "soil_water_index/swi-static_global_12.5km_daily_v3/c_gls_SWI-STATIC-CI_2007----2017_GLOBE_SWI-GLDAS_V1.1.1_nc.json5",
        ),
        (
            (
                test_data
                / "soil_water_index/swi-static_global_12.5km_daily_v3/c_gls_SWI-STATIC-CI_201101010000_GLOBE_SWI-GLDAS_V1.1.1.nc",
            ),
            test_reference
            / "soil_water_index/swi-static_global_12.5km_daily_v3/c_gls_SWI-STATIC-CI_201101010000_GLOBE_SWI-GLDAS_V1.1.1_nc.json5",
        ),
        (
            (
                test_data
                / "soil_water_index/swi-static_global_12.5km_daily_v3/c_gls_SWI-STATIC-TC_201501010000_GLOBE_GTOPO30_V1.1.1.nc",
            ),
            test_reference
            / "soil_water_index/swi-static_global_12.5km_daily_v3/c_gls_SWI-STATIC-TC_201501010000_GLOBE_GTOPO30_V1.1.1_nc.json5",
        ),
        # ssm_europe_1km_daily_v1
        (
            (
                test_data
                / "surface_soil_moisture/ssm_europe_1km_daily_v1/c_gls_SSM1km_201909030000_CEURO_S1CSAR_V1.1.1.nc",
            ),
            test_reference
            / "surface_soil_moisture/ssm_europe_1km_daily_v1/c_gls_SSM1km_201909030000_CEURO_S1CSAR_V1.1.1_nc.json5",
        ),
        # wb_global_1km_10daily_v2
        (
            (
                test_data
                / "water_bodies/wb_global_1km_10daily_v2/c_gls_WB_200109110000_GLOBE_VGT_V2.1.1.nc",
            ),
            test_reference
            / "water_bodies/wb_global_1km_10daily_v2/c_gls_WB_200109110000_GLOBE_VGT_V2.1.1_nc.json5",
        ),
        # wb_global_300m_10daily_v1
        (
            (
                test_data
                / "water_bodies/wb_global_300m_10daily_v1/c_gls_WB300_201902210000_GLOBE_PROBAV_V1.0.1.nc",
            ),
            test_reference
            / "water_bodies/wb_global_300m_10daily_v1/c_gls_WB300_201902210000_GLOBE_PROBAV_V1.0.1_nc.json5",
        ),
        # lc_global_100m_yearly_v3
        (
            (test_data / "dynamic_land_cover/lc_global_100m_yearly_v3/2018",),
            test_reference
            / "dynamic_land_cover/lc_global_100m_yearly_v3/PROBAV_LC100_global_v3.0.1_2018-conso_EPSG-4326.json5",
        ),
        # toc_global_300m_daily_v2
        (
            (
                test_data
                / "top-of-canopy_reflectances/toc_global_300m_daily_v2/cgl_TOC_20190104000021_X33Y07_S3A_v2.3.4.nc",
            ),
            test_reference
            / "top-of-canopy_reflectances/toc_global_300m_daily_v2/cgl_TOC_20190104000021_X33Y07_S3A_v2.3.4_nc.json5",
        ),
        (
            (
                test_data
                / "top-of-canopy_reflectances/toc_global_300m_daily_v2/cgl_TOC_20190129233203_X35Y03_S3B_v2.3.4_cog",
            ),
            test_reference
            / "top-of-canopy_reflectances/toc_global_300m_daily_v2/cgl_TOC_20190129233203_X35Y03_S3B_v2.3.4_cog.json5",
        ),
        # lsp_global_300m_yearly_v1
        (
            (
                test_data
                / "vegetation_phenology_and_productivity_parameters/lsp_global_300m_yearly_v1/c_gls_LSP300-AMPL-S2_202301010000_GLOBE_OLCI_V1.0.1.tiff",
            ),
            test_reference
            / "vegetation_phenology_and_productivity_parameters/lsp_global_300m_yearly_v1/c_gls_LSP300-AMPL-S2_202301010000_GLOBE_OLCI_V1.0.1_cog.json5",
        ),
        # lcm_global_10m_yearly_v1
        (
            (test_data / "dynamic_land_cover/lcm_global_10m_yearly_v1/2020/N36E117/",),
            test_reference
            / "dynamic_land_cover/lcm_global_10m_yearly_v1/LCFM_LCM-10_V100_2020_N36E117.json5",
        ),
        # eta_global_300m_10daily_v1
        (
            (test_data / "evapotranspiration/eta_global_300m_10daily_v1/",),
            test_reference
            / "evapotranspiration/eta_global_300m_10daily_v1/clms_ETA300_202106010000_GLOBE_S3_V1.0.1_cog.json5",
        ),
        # hf_global_300m_daily_v1
        (
            (test_data / "evapotranspiration/hf_global_300m_daily_v1/",),
            test_reference
            / "evapotranspiration/hf_global_300m_daily_v1/clms_HF300_202106010000_GLOBE_S3_V1.0.1_cog.json5",
        ),
        (
            (
                test_data
                / "snow_cover_extent/sce_global_1km_daily_v1/c_gls_SCE_202511220000_GLOBE_VIIRS_V1.0.1.nc",
            ),
            test_reference
            / "snow_cover_extent/sce_global_1km_daily_v1/c_gls_SCE_202511220000_GLOBE_VIIRS_V1.0.1.nc.json5",
        ),
        #############
        ## HRLVLCC ##
        #############
        # crop-types
        (
            (
                test_data
                / "landcover_landuse/crop_types/clms_vlcc_crop-types_europe_10m_yearly_v1/CLMS_HRLVLCC_CTY_S2019_R10m_E65N17_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/crop_types/clms_vlcc_crop-types_europe_10m_yearly_v1/CLMS_HRLVLCC_CTY_S2019_R10m_E65N17_03035_V01_R00.json5",
        ),
        # crop-types-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/crop_types/clms_vlcc_crop-types-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CTYCL_S2020_R10m_E64N16_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/crop_types/clms_vlcc_crop-types-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CTYCL_S2020_R10m_E64N16_03035_V01_R00.json5",
        ),
        # bare-soil-after
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-after_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSA_S2019_R10m_E64N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-after_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSA_S2019_R10m_E64N15_03035_V01_R00.json5",
        ),
        # bare-soil-after-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-after-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSACL_S2018_R10m_E64N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-after-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSACL_S2018_R10m_E64N15_03035_V01_R00.json5",
        ),
        # bare-soil-before
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-before_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSB_S2017_R10m_E63N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-before_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSB_S2017_R10m_E63N15_03035_V01_R00.json5",
        ),
        # bare-soil-before-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-before-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSBCL_S2017_R10m_E63N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_bare-soil-before-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPBSBCL_S2017_R10m_E63N15_03035_V01_R00.json5",
        ),
        # cropping-seasons-types
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_cropping-seasons-types_europe_10m_3yearly_v1/CLMS_HRLVLCC_CPCST_P2019-2021_R10m_E10N25_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_cropping-seasons-types_europe_10m_3yearly_v1/CLMS_HRLVLCC_CPCST_P2019-2021_R10m_E10N25_03035_V01_R00.json5",
        ),
        # cropping-seasons
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_cropping-seasons_europe_10m_yearly_v1/CLMS_HRLVLCC_CPCSY_S2018_R10m_E63N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_cropping-seasons_europe_10m_yearly_v1/CLMS_HRLVLCC_CPCSY_S2018_R10m_E63N15_03035_V01_R00.json5",
        ),
        # fallow-land-duration
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-duration_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLD_P2019-2023_R10m_E11N25_03035_V01_R00",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-duration_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLD_P2019-2023_R10m_E11N25_03035_V01_R00.json5",
        ),
        # fallow-land-duration-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-duration-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLDCL_P2017-2021_R10m_E11N25_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-duration-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLDCL_P2017-2021_R10m_E11N25_03035_V01_R00.json5",
        ),
        # fallow-land-presence
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-presence_europe_laea_10m_yearly_v1/CLMS_HRLVLCC_CPFLP_S2019_R10m_E64N16_03035_V01_R00",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-presence_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLP_S2019_R10m_E64N16_03035_V01_R00.json5",
        ),
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-presence_dom_utm_10m_yearly_v1/CLMS_HRLVLCC_CPFLP_S2020_R10m_MQ_32620_V01_R00",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-presence_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLP_S2020_R10m_MQ_32620_V01_R00.json5",
        ),
        (
            (test_data / "tar/CLMS_HRLVLCC_CPFLP_S2017_R10m_E65N19_03035_V01_R00.tar",),
            test_reference
            / "tar/CLMS_HRLVLCC_CPFLP_S2017_R10m_E65N19_03035_V01_R00.json5",
        ),
        # fallow-land-presence-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-presence-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLPCL_S2019_R10m_E63N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/cropping_patterns/clms_vlcc_fallow-land-presence-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_CPFLPCL_S2019_R10m_E63N15_03035_V01_R00.json5",
        ),
        # grassland
        (
            (
                test_data
                / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland_europe_10m_yearly_v1/CLMS_HRLVLCC_GRA_S2017_R10m_E64N16_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland_europe_10m_yearly_v1/CLMS_HRLVLCC_GRA_S2017_R10m_E64N16_03035_V01_R00.json5",
        ),
        # grassland-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_GRACL_S2020_R10m_E63N16_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland-confidence-layer_europe_10m_yearly_v1/CLMS_HRLVLCC_GRACL_S2020_R10m_E63N16_03035_V01_R00.json5",
        ),
        # grassland-change
        (
            (
                test_data
                / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland-change_europe_20m_3yearly_v1/CLMS_HRLVLCC_GRAC_C2018-2021_R20m_E63N15_03035_V01_R00/",
            ),
            test_reference
            / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland-change_europe_20m_3yearly_v1/CLMS_HRLVLCC_GRAC_C2018-2021_R20m_E63N15_03035_V01_R00.json5",
        ),
        # grassland-change-confidence-layer
        (
            (
                test_data
                / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland-change-confidence-layer_europe_20m_3yearly_v1/CLMS_HRLVLCC_GRACCL_C2018-2021_R20m_E64N16_03035_V01_R00",
            ),
            test_reference
            / "landcover_landuse/grassland_and_herbaceous/clms_vlcc_grassland-change-confidence-layer_europe_20m_3yearly_v1/CLMS_HRLVLCC_GRACCL_C2018-2021_R20m_E64N16_03035_V01_R00.json5",
        ),
    ],
)
def test_builder(files, reference):
    assert all(p.exists() for p in files)

    builder = MetadataBuilder(
        storage=LocalFileSystem(), settings=Settings(link=LinkSettings(value="test"))
    )
    m = builder.build(files)
    # print(m.model_dump(mode="json"))
    compare_with_reference_file(m, reference)


@pytest.mark.parametrize(
    "file_name",
    [
        "c_gls_SCE500_201703010000_CEURO_MODIS_V1.0.1.nc",
        "c_gls_SCE_201801090000_NHEMI_VIIRS_V1.0.1.nc",
        "c_gls_SWE5K_200601010000_NHEMI_SSMIS_V1.0.2.nc",
        "c_gls_LSWT_201611010000_GLOBE_SLSTRA_v1.0.2.nc",
        "c_gls_LSWT_200205110000_GLOBE_AATSR_v1.0.2.nc",
        "c_gls_WB100_202010010000_GLOBE_S2_V1.0.1.nc",
        "c_gls_WB300_202010010000_GLOBE_S2_V2.0.1.nc",
        "c_gls_LWQ100_201812210000_GLOBAL_MSI_V1.3.nc",
        "c_gls_LWQ300_201604210000_GLOBE_OLCI_V1.3.0.nc",
        "c_gls_LWQ300_200205110000_GLOBE_MERIS_V1.3.0.nc",
        "c_gls_LIE250_201703150000_Baltic_MODIS_V1.0.1.nc",
        "c_gls_LIE-NH_202104010000_NHEMI_SLSTR_V1.1.1.nc",
        "c_gls_LWQ1km_201604210000_GLOBE_OLCI_V1.2.nc",  # clms_global_lwq_1km_v1_10daily-nrt_netcdf
        "c_gls_SWE5K_202407010000_NHEMI_SSMIS_V2.0.1.nc",  # clms_global_swe_5km_v2_daily_netcdf
        "c_gls_SWE5K_202510140000_NHEMI_AMSR-2_V2.1.1.nc",  # clms_global_swe_5km_v2_daily_netcdf
        "c_gls_LWQ300_202409010000_GLOBE_OLCI_V2.0.0.nc",  # clms_global_lwq_300m_v2_10daily-nrt_netcdf
        "c_gls_LWQ1km_200205110000_GLOBE_MERIS_V1.1.nc",  # clms_global_lwq_1km_v1_10daily-reproc_netcdf
        "c_gls_LWQ100_202409010000_GLOBAL_MSI_V2.0.nc",  # clms_global_lwq_100m_v2_10daily-nrt_netcdf
        "c_gls_LIE250_202402190000_CEURO_VIIRS_V2.2.1.nc",
    ],
)
def test_cls_netcdf_products(file_name):
    with open(
        test_root / "reference" / "cls" / "cls_datasets_expected_metadata.json5", "r"
    ) as f:
        expected_data = [
            d for d in pyjson5.load(f) if d.get("name") == file_name.replace(".nc", "")
        ][0]

    builder = MetadataBuilder(storage=LocalFileSystem(), settings=Settings())
    m = builder.build((test_data / "cls" / file_name,))

    compare_with_reference(m, expected_data)


@pytest.mark.parametrize(
    ("path", "reference"),
    [
        (
            test_data
            / "river_and_lake_water_level/wl-lakes_global_vector_daily_v2/c_gls_WL_202412050703_1300000000166_ALTI_V2.2.0.json",
            test_reference
            / "river_and_lake_water_level/wl-lakes_global_vector_daily_v2/c_gls_WL_202412050703_1300000000166_ALTI_V2.2.0.json",
        ),
        (
            test_data
            / "river_and_lake_water_level/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json",
            test_reference
            / "river_and_lake_water_level/wl-rivers_global_vector_daily_v2/c_gls_WL_202411291440_0000000000108_ALTI_V2.2.0.json5",
        ),
    ],
)
def test_water_level_global_vector_daily(path, reference):
    assert path.exists()
    builder = MetadataBuilder(storage=LocalFileSystem(), settings=Settings())
    m = builder.build((path,))

    compare_with_reference_file(m, reference)


def compare_with_reference_file(m: Metadata, reference: Path):
    """
    Compare the metadata model with a reference

    :param m: metadata model
    :param reference: path to reference file
    :return:
    """
    try:
        with open(reference) as f:
            expected = pyjson5.load(f)
    except FileNotFoundError as e:
        dump = m.model_dump(mode="json")
        dump["attributes"] = {a["name"]: a["value"] for a in dump["attributes"]}
        p_dump = reference.parent / (reference.stem + "_generated" + reference.suffix)
        p_dump.parent.mkdir(parents=True, exist_ok=True)
        with p_dump.open("w") as f:
            pyjson5.dump(dump, f)
        raise e
    compare_with_reference(m, expected)


def compare_with_reference(m: Metadata, expected: dict):
    """
    Compare the metadata with a reference dictionary.

    :param m: metadata model
    :param expected: reference dictionary
    :return:
    """
    m_dict = m.model_dump()
    expected_attributes = expected.pop("attributes")

    for k, v in expected.items():
        assert v == m_dict.get(k)

    attributes = {a["name"]: a["value"] for a in m_dict["attributes"]}
    assert {
        k: v for k, v in attributes.items() if k in expected_attributes
    } == expected_attributes
