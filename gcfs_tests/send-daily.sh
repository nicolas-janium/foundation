payload_path="/home/nicolas/projects/janium/python/function_tests/send_daily_tasks.json"
payload=$(jq . "$payload_path")
# echo $payload

gcloud pubsub topics publish send-daily-tasks-topic --message "$payload"