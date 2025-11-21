ARG BASE_IMAGE="ghcr.io/osgeo/gdal:ubuntu-small-latest"

FROM ${BASE_IMAGE}
ARG PACKAGE_NAME

ENV CACHE_DIR=/var/cache/clms-metadata/

COPY dist/${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
RUN apt update && apt install -y \
    libexpat1 \
    python3-pip
RUN pip install --break-system-package --no-cache-dir /tmp/${PACKAGE_NAME}

ADD https://raw.githubusercontent.com/copernicus-land/EOAssets/1990be98767b60386b31bb273b50548cf3ecff1d/EOassetNameList.yaml ${CACHE_DIR}

ENTRYPOINT ["clms-metadata"]