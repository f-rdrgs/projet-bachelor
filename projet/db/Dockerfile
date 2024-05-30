FROM postgres:15.7-bullseye

LABEL author="Rodrigues dos Santos Fabio"

COPY *.sql /docker-entrypoint-initdb.d/

WORKDIR /data/

COPY ./data/*.csv .