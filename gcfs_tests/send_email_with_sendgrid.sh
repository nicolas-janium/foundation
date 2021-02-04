payload_path="/home/nicolas/projects/janium/python/function_tests/send_email_with_sendgrid.json"
payload=$(jq . "$payload_path")
# echo $payload

gcloud pubsub topics publish send-email-with-sendgrid-topic --message "$payload"
