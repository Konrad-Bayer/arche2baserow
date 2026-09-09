#!/bin/bash

docker run \
  --rm \
  --name arche-ingest \
  -v `pwd`/to_ingest:/data \
  --entrypoint arche-import-binary \
  acdhch/arche-ingest \
  /data \
  https://id.acdh.oeaw.ac.at/konradbayer \
  https://arche-curation.acdh-dev.oeaw.ac.at/api \
  $ARCHE_LOGIN \
  $ARCHE_PASSWORD \
  --skip not_exist \
  2>&1 | tee ./meta/import_binary.log
