ARG BASE_IMAGE="python:3.12-slim"

FROM ${BASE_IMAGE}
ARG PACKAGE_NAME

COPY dist/${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
RUN apt update && apt install -y libexpat1
RUN pip install --no-cache-dir /tmp/${PACKAGE_NAME}

ENTRYPOINT ["clms-metadata"]