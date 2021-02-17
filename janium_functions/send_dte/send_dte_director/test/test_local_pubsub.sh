#! /bin/bash

RAW_MESSAGE="Hello, World!"
MESSAGE_BASE64=$(echo -n ${RAW_MESSAGE} | base64)

EVENT_PAYLOAD=$(
  sed -e \
    "s|__DATA_BASE64_PLACEHOLDER__|${MESSAGE_BASE64}|g" \
    /home/nicolas/projects/janium/foundation/janium_functions/send_dte/send_dte_director/test_local_pubsub_payload.json
)

curl -X POST \
  -H'Content-type: application/json' \
  -d "${EVENT_PAYLOAD}" \
  "http://localhost:5000"
