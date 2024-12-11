# Usage
## CLI
The Python package exposes the `clms-metadata` entrypoint command to access the command-line interface
More information about all commands of the CLI can be found by using the `--help flag`.

```console
$ clms-metadata --help
Usage: clms-metadata COMMAND

╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ odata                                                                        │
│ product                                                                      │
│ --help -h  Display this message and exit.                                    │
│ --version  Display application version.                                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

The application can be configured by using environment variables. For a more detailed explanation of the configuration options, check the [configuration](configuration) page.

### OData
The OData subcommand allows you to generate OData metadata for a product.
All you need to provide is the path of the product file or product directory. 
By default, the generated metadata is written to the `stdout` stream.
Optionally, you can specify an output directory using the `--output` flag. This directory is then used to write the generated metadata to instead.

Example of `clms-metadata odata create` command:
```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_ENDPOINT_URL=...

clms-metadata odata create 's3://CLMS-ARCHIVE-INGESTION/geotiff/ndvi/ndvi_1km_v3_10daily/2020/20200321/c_gls_NDVI_202003210000_GLOBE_PROBAV_V3.0.1_geotiff/' --output=/tmp/CLMS/ndvi_1km_v3_10daily/
```

## Docker
The commands of the CLI can be accessed directly from the Docker image. The Docker image uses the `clms-metadata` command as the entrypoint, so you can specify the subcommands and parameters directly after the image name.
For example, use the following command to run the OData metadata generation:

```bash
docker run --rm -a stdout -a stderr --security-opt seccomp=unconfined \
-e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_ENDPOINT_URL \
vito-docker.artifactory.vgt.vito.be/clms_metadata \
odata create s3://CLMS-ARCHIVE-INGESTION/netcdf/ndvi/ndvi_1km_v3_10daily/2020/20200321/c_gls_NDVI_202003210000_GLOBE_PROBAV_V3.0.1.nc
```

### Caveat with netCDF
When running the application from its Docker image and reading netCDF files from a /vsi file system (like S3, cURL, ...), you'll have to adjust the security policies.
Otherwise, you'll get the following error message:

```text
 Opening a /vsi file with the netCDF driver requires Linux userfaultfd to be available. 
 If running from Docker, --security-opt seccomp=unconfined might be needed.
```

More specifically, the GDAL netCDF driver requires the `userfaultd` system call, which is not allowed by Docker by default.
More information about the netCDF support in GDAL can be found in the [GDAL documentation](https://gdal.org/en/latest/drivers/raster/netcdf.html#vsi-virtual-file-system-api-support).

Adding the `--security-opt seccomp=unconfined` option to the Docker run command will allow the process in the Docker container to access the `userfaultd` system call.
A custom [security profile](https://docs.docker.com/engine/security/seccomp/) to specifically whitelist the `userfaultd` system call could also work.