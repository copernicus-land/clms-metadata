FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.3 as builder
ARG PACKAGE_NAME

COPY dist/${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
RUN apt update && apt install --no-install-recommends -y python3-pip python3-venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir /tmp/${PACKAGE_NAME}

FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.3
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["clms-metadata"]