from mitmproxy import http
from mitmproxy import ctx
import prometheus_client
import base64
import json

# Prometheus counters
input_token_counter = prometheus_client.Counter('input_tokens_processed', 'Number of input tokens processed')
output_token_counter = prometheus_client.Counter('output_tokens_processed', 'Number of output tokens processed')

class TokenCounter:
    def request(self, flow: http.HTTPFlow) -> None:
        request_body = flow.request.content.decode('utf-8')
        input_tokens = len(request_body.split())  # Simple token counting
        input_token_counter.inc(input_tokens)
        ctx.log.info(f"Input tokens: {input_tokens}")

    def response(self, flow: http.HTTPFlow) -> None:
        response_body = flow.response.content.decode('utf-8')
        try:
            data = json.loads(response_body)
            output_base64_str = data[0]['base64']
            output_tokens = len(output_base64_str) / 1000  # Example token count based on base64 length
            output_token_counter.inc(output_tokens)
            ctx.log.info(f"Output tokens: {output_tokens}")
        except (json.JSONDecodeError, KeyError) as e:
            ctx.log.error(f"Error processing response: {e}")

class TrafficLogger:
    def request(self, flow: http.HTTPFlow) -> None:
        flow.request.host = "localhost"
        flow.request.port = 8888
        request_body = flow.request.content.decode('utf-8', errors='replace')
        ctx.log.info(f"Intercepted Request: {request_body}")

    def response(self, flow: http.HTTPFlow) -> None:
        response_body = flow.response.content.decode('utf-8', errors='replace')
        ctx.log.info(f"Intercepted Response: {response_body}")

addons = [
    TrafficLogger(),
    TokenCounter()
]

# Start Prometheus metrics server
prometheus_client.start_http_server(9001)

