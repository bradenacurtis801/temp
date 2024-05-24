FROM python:3.9-slim

# Install mitmproxy and Prometheus client
RUN pip install mitmproxy prometheus_client

# Copy the mitmproxy script
COPY token_counter.py /scripts/token_counter.py

# Expose the ports for mitmproxy and Prometheus metrics
EXPOSE 8080
EXPOSE 9001

# Set the entry point to mitmdump with the script and specify the port
ENTRYPOINT ["mitmdump", "-s", "/scripts/token_counter.py", "-p", "8080"]

