#!/bin/bash

docker run \
  --rm \
  --name arche-ingest \
  -v `pwd`/rdf:/data \
  --entrypoint arche-import-metadata \
  acdhch/arche-ingest \
  --concurrency 4 \
  /data/<file>.ttl \
  https://arche-curation.acdh-dev.oeaw.ac.at/api \
  $ARCHE_LOGIN \
  $ARCHE_PASSWORD \
  2>&1 | tee ./meta/import_metadata.log
