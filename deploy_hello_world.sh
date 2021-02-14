#!/bin/sh
gcloud functions deploy function-1 --region=us-central1 --entry-point=main --runtime=python38 --trigger-http --allow-unauthenticated --source=./gcfs/hello_world/