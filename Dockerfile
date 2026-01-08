ARG BASE_IMAGE="ghcr.io/osgeo/gdal:ubuntu-small-latest"

FROM ${BASE_IMAGE}

ENV CACHE_DIR=/var/cache/clms-metadata/
ENV VENV_DIR=/opt/venv

RUN apt update && apt install -y \
    libexpat1 \
    python3-pip \
    python3-venv

ARG PACKAGE_NAME
COPY dist/${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
RUN python3 -m venv --system-site-packages ${VENV_DIR} &&  \
    . /opt/venv/bin/activate &&  \
    pip install --no-cache-dir /tmp/${PACKAGE_NAME}

ENV PATH="${VENV_DIR}/bin:$PATH"

ADD https://raw.githubusercontent.com/copernicus-land/EOAssets/b158ada7270cd8df4c44bda3d06e206e7303d32a/EOassetNameList.yaml ${CACHE_DIR}

ENTRYPOINT ["clms-metadata"]