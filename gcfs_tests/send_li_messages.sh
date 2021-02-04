payload_path="/home/nicolas/projects/janium/python/function_tests/send_li_messages.json"
payload=$(jq . "$payload_path")
# echo $payload

gcloud pubsub topics publish send-li-message-topic --message "$payload"