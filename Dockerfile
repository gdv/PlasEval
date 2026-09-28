FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install from the current repo state, then discard the sources
COPY . /tmp/PlasEval
RUN pip install /tmp/PlasEval \
    && rm -rf /tmp/PlasEval

LABEL org.opencontainers.image.source="https://github.com/gdv/PlasEval" \
    org.opencontainers.image.description="PlasEval - evaluation and comparison of plasmid binning"

WORKDIR /data
ENTRYPOINT ["plaseval"]
CMD ["--help"]