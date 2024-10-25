# clms-metadata tool

The `clms-metadata` tool is a Python package and command-line interface (CLI) to generate OData product metadata.
The tool supports multiple file systems (local file system, S3) and can combine different metadata sources.


## Configuration
The configuration of the application is handled by `pydantic-settings`. This makes it possible to configure the application
by providing a YAML file, or overwriting default settings values via environment variables.

## Metadata sources
The application supports multiple metadata sources:
 - information included in file names
 - embedded metadata in raster files, using rioxarray
 - metadata stored in Elasticsearch
 - static metadata configured in the settings

These metadata sources can be configured in the settings as a chain.
This means that you can select which metadata sources should be used, and in which order these should be applied. 
Each metadata source will extract specific supported information, filling in missing information in the product metadata.

## Usage
The application takes the file paths belonging to a product as arguments. Based on these file paths, the correct 
file system is selected. As mentioned above, the configured metadata sources will then be used to extract the 
product metadata and compile it into an OData metadata document.
The output of the CLI application can be chosen to be either a file or to be written to `stdout`.
