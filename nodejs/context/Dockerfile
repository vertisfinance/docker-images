FROM vertisfinance/base

MAINTAINER Richard Bann richard.bann@vertis.com

RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           ca-certificates \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           curl \
           build-essential \
    && curl -sL https://deb.nodesource.com/setup_4.x | bash - \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y nodejs \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get purge -y \
           curl \
           # build-essential \
    && DEBIAN_FRONTEND=noninteractive apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
