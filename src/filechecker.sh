#!/bin/bash

docker run \
  --rm \
  -v `pwd`/filechecker/reports:/reports \
  -v `pwd`/data:/data \
  --entrypoint arche-filechecker \
  acdhch/arche-ingest \
  --csv --html /data /reports