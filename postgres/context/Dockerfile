FROM vertisfinance/base

MAINTAINER Richard Bann richard.bann@vertis.com

ENV PG_VERSION=9.4

RUN set -x \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           postgresql-common \
    && sed -ri 's/#(create_main_cluster) .*$/\1 = false/' \
       /etc/postgresql-common/createcluster.conf \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
           postgresql-${PG_VERSION} \
           postgresql-contrib-${PG_VERSION} \
    && DEBIAN_FRONTEND=noninteractive apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /usr/lib/postgresql/9.4/bin:$PATH

RUN rmdir /run/postgresql
RUN rmdir /var/lib/postgresql
RUN rmdir /var/log/postgresql

RUN userdel postgres
