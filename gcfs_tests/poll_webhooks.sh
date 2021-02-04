payload_path="/home/nicolas/projects/janium/python/function_tests/poll_webhooks.json"
payload=$(jq . "$payload_path")

gcloud pubsub topics publish poll-webhook-topic --message "$payload"
