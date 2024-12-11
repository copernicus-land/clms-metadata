SENSOR_PLATFORM_MAPPING = {  # Some files have no platform metadata, so we need to derive it from the sensor name
    "OLCI": "SENTINEL-3"
}

IDENTIFIER_TAG_DATASET_IDENTIFIER_MAPPING = {
    'lie_v1_250m': 'lie_baltic_250m_daily_v{version_major}',
    'sce500_v1_0.005degree': 'sce_europe_500m_daily_v{version_major}',
    'lie_nh_v1_500m': 'lie_northernhemisphere_500m_daily_v{version_major}',
    #'lswt_v1_1km': 'lswt-offline_global_1km_10daily_v{version_major}',
    #'lswt_v1_1km': 'lswt-nrt_global_1km_10daily_v{version_major}',
    'lwq_v1_100': 'lwq-nrt_global_100m_10daily_v{version_major}',
    #'lwq_v1_300': 'lwq-reproc_global_300m_10daily_v{version_major}',
    #'lwq_v1_300': 'lwq-nrt_global_300m_10daily_v{version_major}',
    'sce_v1_0.01degree': 'sce_northernhemisphere_1km_daily_v{version_major}',
    'swe_V1_5km': 'swe_northernhemisphere_5km_daily_v{version_major}',
    'wb_v1_100m': 'wb_global_100m_monthly_v{version_major}',
    'wb_v2_300m': 'wb_global_300m_monthly_v{version_major}',
    'ndvi_v3_1km': "ndvi_global_1km_10daily_v{version_major}",
    'fapar300_v1_333m': "fapar_global_300m_10daily_v{version_major}"
}