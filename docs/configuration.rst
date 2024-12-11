Configuration
-------------

The configuration of the application is handled by `pydantic-settings`. This makes it possible to configure the application
by providing a YAML file, or overwriting default settings values via environment variables.
Environment variable names are the same as the field name in the :obj:`~clms_metadata.config.Settings` model below.
For nested settings, the ``__`` delimiter should be used. For example, to adjust the geometry precision, you can override the default by setting this environment variable:

    GEOMETRY__PRECISION=0.0001

Settings
========
.. autopydantic_settings:: clms_metadata.config.Settings

Elasticsearch
=============
.. autopydantic_settings:: clms_metadata.config.ElasticsearchSettings

Geometry
========
.. autopydantic_settings:: clms_metadata.config.GeometrySettings

Link
====
.. autopydantic_settings:: clms_metadata.config.LinkSettings

Metadata
========
.. autopydantic_settings:: clms_metadata.config.MetadataSettings

S3
==
.. autopydantic_settings:: clms_metadata.config.S3Settings


