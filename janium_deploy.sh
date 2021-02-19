#!/bin/sh

echo "Deploying function-1..."
gcloud functions deploy hello_world --region=us-central1 --entry-point=main --runtime=python38 --trigger-http --allow-unauthenticated --source=./janium_functions/hello_world
