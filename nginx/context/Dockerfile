FROM vertisfinance/base

MAINTAINER Richard Bann richard.bann@vertis.com

RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           nginx \
    && DEBIAN_FRONTEND=noninteractive apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
