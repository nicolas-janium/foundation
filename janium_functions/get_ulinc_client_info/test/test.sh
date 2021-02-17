payload_path="/home/nicolas/projects/janium/main/gcfs/get_ulinc_client_info/test/payload.json"
payload=$(jq . "$payload_path")

curl --header "Content-Type: application/json" \
    --request POST \
    --data "${payload}" \
    --url http://localhost:8080