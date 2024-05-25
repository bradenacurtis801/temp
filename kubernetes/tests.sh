
generate_img() {
  local domain="$1"

  curl -X POST "http://${domain}/v1/generation/text-to-image" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "elephant",
    "negative_prompt": "",
    "style_selections": [
      "Fooocus V2",
      "Fooocus Enhance",
      "Fooocus Sharp"
    ],
    "save_meta": true,
    "meta_scheme": "fooocus",
    "save_extension": "png",
    "save_name": "",
    "read_wildcards_in_order": false,
    "require_base64": true,
    "async_process": false,
    "webhook_url": ""
  }'
}



get_token_stats() {
  local POD_IP='10.42.2.40'
  curl $POD_IP:9001/metrics
}
