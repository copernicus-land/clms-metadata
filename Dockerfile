ARG BASE_IMAGE='ghcr.io/osgeo/gdal:alpine-normal-3.10.0'

FROM ${BASE_IMAGE} AS builder
ARG PACKAGE_NAME

COPY dist/${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
RUN apk add py3-pip python3-dev gcc musl-dev g++ geos-dev
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir /tmp/${PACKAGE_NAME}

FROM ${BASE_IMAGE}
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["clms-metadata"]