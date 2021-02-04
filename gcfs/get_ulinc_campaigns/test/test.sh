payload_path="./gcfs/get_ulinc_campaigns/test/payload.json"
payload=$(jq . "$payload_path")

curl --header "Content-Type: application/json" \
    --request POST \
    --data "${payload}" \
    --url http://localhost:8080