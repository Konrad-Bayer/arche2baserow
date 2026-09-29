#!/bin/bash

docker run \
  --rm \
  -v `pwd`/filechecker/reports:/reports \
  -v /mnt/projects01/ACDH_ARCHE/staging/KonradBayer_27121/data/KB_2026_Digitale_Transformation:/data \
  --entrypoint arche-filechecker \
  acdhch/arche-ingest \
  --csv --html /data /reports