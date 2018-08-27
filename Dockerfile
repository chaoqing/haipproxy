FROM alpine:3.7

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN apk upgrade --no-cache \
  && apk add --no-cache \
    musl \
    build-base \
    python3 \
    python3-dev \
    postgresql-dev \
    bash \
    git \

    redis \

    squid \
    libxml2-dev \
    libxml2 \
    libxslt-dev \
    libxslt \
    libffi-dev \
    python3-dev \
  && pip3 install --no-cache-dir --upgrade pip && \

  cd /usr/bin \
  && ln -sf python3 python \
  && ln -sf pip3 pip \

  && rm -rf /var/cache/* \
  && rm -rf /root/.cache/*

COPY requirements.txt ./
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt && rm requirements.txt

COPY . /haipproxy
WORKDIR /haipproxy
RUN sed -i 's/http_access deny all/http_access allow all/g' /etc/squid/squid.conf \
    && cp /etc/squid/squid.conf /etc/squid/squid.conf.backup \
    && chmod +x run.sh

CMD ["bash", "./run.sh"]
