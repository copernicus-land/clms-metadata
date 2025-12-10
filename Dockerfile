ARG BASE_IMAGE="ghcr.io/osgeo/gdal:ubuntu-small-latest"

FROM ${BASE_IMAGE}
ARG PACKAGE_NAME

ENV CACHE_DIR=/var/cache/clms-metadata/

COPY dist/${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
RUN apt update && apt install -y \
    libexpat1 \
    python3-pip
RUN pip install --break-system-package --no-cache-dir /tmp/${PACKAGE_NAME}

ADD https://raw.githubusercontent.com/copernicus-land/EOAssets/b158ada7270cd8df4c44bda3d06e206e7303d32a/EOassetNameList.yaml ${CACHE_DIR}

ENTRYPOINT ["clms-metadata"]