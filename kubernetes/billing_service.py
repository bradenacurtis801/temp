from prometheus_api_client import PrometheusConnect

# Set the Prometheus URL using the service name and port from your Kubernetes cluster
PROMETHEUS_URL = "http://10.10.231.2:9090/"  # Adjusted with the correct Cluster IP and port

# Initialize Prometheus client
prometheus = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

# Define the rate per million tokens
RATE_PER_MILLION_TOKENS = 0.25

def get_token_usage():
    input_tokens_query = 'sum(input_tokens_processed)'
    output_tokens_query = 'sum(output_tokens_processed)'
    
    input_tokens = prometheus.custom_query(query=input_tokens_query)
    output_tokens = prometheus.custom_query(query=output_tokens_query)
    
    total_input_tokens = float(input_tokens[0]['value'][1]) if input_tokens else 0
    total_output_tokens = float(output_tokens[0]['value'][1]) if output_tokens else 0
    
    return total_input_tokens, total_output_tokens

def calculate_cost(input_tokens, output_tokens):
    total_tokens = input_tokens + output_tokens
    cost = (total_tokens / 1_000_000) * RATE_PER_MILLION_TOKENS
    return cost

def simulate_create_invoice(customer_id, amount):
    # Simulate invoice creation by printing the details
    print(f"Simulating invoice creation...")
    print(f"Customer ID: {customer_id}")
    print(f"Amount: ${amount:.2f}")
    print(f"Description: Token Usage Billing")

def main():
    input_tokens, output_tokens = get_token_usage()
    print(f"Input Tokens: {input_tokens}")
    print(f"Output Tokens: {output_tokens}")
    
    cost = calculate_cost(input_tokens, output_tokens)
    print(f"Total Cost: ${cost:.2f}")
    
    customer_id = "your_stripe_customer_id"
    simulate_create_invoice(customer_id, cost)

if __name__ == "__main__":
    main()

