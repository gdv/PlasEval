# Stage 1: build pixi environment with all dependencies (network allowed)
FROM ghcr.io/prefix-dev/pixi:0.71.1 AS build

COPY src /app
WORKDIR /app
RUN pixi install
RUN pixi shell-hook  > /shell-hook.sh

# extend the shell-hook script to run the command passed to the container
RUN echo 'exec "$@"' >> /shell-hook.sh

VOLUME ["/data"]
ENTRYPOINT ["/bin/bash", "/shell-hook.sh"]
