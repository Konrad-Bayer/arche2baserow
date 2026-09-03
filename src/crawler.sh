#!/bin/bash

docker run \
  --rm -u `id -u`:`id -g`\
  -v `pwd`:/mnt \
  --entrypoint arche-crawl-meta \
  acdhch/arche-ingest \
  --filecheckerReportDir /mnt/filechecker/reports/2026_09_02_14_48_48 \
  /mnt/rdf \
  /mnt/meta/crawler.ttl \
  /mnt/data \
  https://id.acdh.oeaw.ac.at/konradbayer \
  2>&1 | tee ./meta/crawler.log