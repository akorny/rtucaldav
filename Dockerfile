FROM alpine:3.19.0
RUN apk update && apk upgrade && \
    apk add --no-cache  \
        python3 py3-pip py3-virtualenv \ 
        apache2 apache2-mod-wsgi apache2-utils \
        sed bash git tzdata openssl curl ca-certificates \
        musl-dev gcc cargo
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt
COPY . rtucaldav/
RUN mv rtucaldav/rtucaldav/local_settings_sample.py rtucaldav/rtucaldav/local_settings.py

COPY utilities/radicale-config utilities/radicale.wsgi utilities/rights radicale/

WORKDIR /etc/apache2
RUN rm conf.d/*
COPY utilities/rtucaldav.conf utilities/radicale.conf utilities/basic.conf conf.d/

COPY utilities/crontab /etc/crontabs/root

RUN update-ca-certificates

EXPOSE 80
EXPOSE 5232

ENTRYPOINT ["/bin/bash", "/opt/rtucaldav/startup.sh"]