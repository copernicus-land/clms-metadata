# Usage

## Docker
When running the application from its Docker image and reading netCDF files from a /vsi file system (like S3, cURL, ...), you'll have to adjust the security policies.
Otherwise, you'll get the following error message:

```
 Opening a /vsi file with the netCDF driver requires Linux userfaultfd to be available. 
 If running from Docker, --security-opt seccomp=unconfined might be needed.
```

More specifically, the GDAL netCDF driver requires the `userfaultd` system call, which is not allowed by Docker by default.
More information about the netCDF support in GDAL can be found in the [GDAL documentation](https://gdal.org/en/latest/drivers/raster/netcdf.html#vsi-virtual-file-system-api-support).

Adding the `--security-opt seccomp=unconfined` option to the Docker run command will allow the process in the Docker container to access the `userfaultd` system call.
A custom [security profile](https://docs.docker.com/engine/security/seccomp/) to specifically whitelist the `userfaultd` system call might also work.