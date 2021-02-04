payload_path="/home/nicolas/projects/janium/python/function_tests/send_email_payload.json"
payload=$(jq . "$payload_path")
# echo $payload

gcloud pubsub topics publish send-email-topic --message "$payload"
