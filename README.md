## GPU Usage Billing Script
This project contains a script to collect GPU usage statistics from a Kubernetes cluster and filter the data by namespace. The script uses gRPC to communicate with the Kubernetes Kubelet's pod-resources API and Prometheus to query GPU metrics.

## Features
Retrieves GPU usage metrics for specific namespaces.
Uses Kubernetes' pod-resources API to find which GPUs are assigned to which pods.
Filters GPU metrics by namespace using Prometheus queries.
Outputs GPU utilization for specified namespaces.

## Prerequisites
- Kubernetes cluster with GPU nodes.
- Prometheus server set up to collect GPU metrics.
- Python 3.8 or later.
- gRPC and Prometheus Python libraries.

## Setup Instructions
### 1. Install Python and Required Libraries
Create a virtual environment and install the required Python packages:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate Protobuf Files
Clone the Kubernetes repository to get the protobuf definitions:

```sh
git clone https://github.com/kubernetes/kubernetes.git
cd kubernetes/staging/src/k8s.io/kubelet/pkg/apis/podresources/v1
```

#### Generate the Python code from the .proto file:

```sh
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. api.proto
```

#### Move the generated api_pb2.py and api_pb2_grpc.py files to your project directory:

```sh
cp api_pb2.py api_pb2_grpc.py /path/to/your/project
```

### 3. Prepare the Project Directory
#### Make sure your project directory has the following structure:

```sh
my_project/
├── venv
├── api_pb2.py
├── api_pb2_grpc.py
├── dcgm.py
└── requirements.txt
```

### 4. Create Kubernetes Deployment

#### Create a Kubernetes deployment to run the script:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-usage-billing
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gpu-usage-billing
  template:
    metadata:
      labels:
        app: gpu-usage-billing
    spec:
      containers:
      - name: gpu-usage-billing
        image: your-docker-repo/gpu-usage-billing:latest
        volumeMounts:
        - name: kubelet-socket
          mountPath: /var/lib/kubelet/pod-resources
          readOnly: true
        securityContext:
          privileged: true
        env:
        - name: PROMETHEUS_URL
          value: "http://prometheus-server:9090"
      volumes:
      - name: kubelet-socket
        hostPath:
          path: /var/lib/kubelet/pod-resources
          type: Directory
      restartPolicy: Always
      serviceAccountName: your-service-account
```

### 5. Run the Script
#### To run the script, use the following command:

```sh
sudo /home/ubuntu/temp/venv/bin/python3 dcgm.py
```

#### Script Overview
##### The script dcgm.py performs the following tasks:

- Connects to the Kubelet's pod-resources API to get a list of GPU devices assigned to pods.
- Queries Prometheus to get GPU utilization metrics.
- Filters the metrics based on the namespace and outputs the results.

#### Example dcgm.py Script
```python
import grpc
import requests
import api_pb2
import api_pb2_grpc

PROMETHEUS_URL = 'http://your-prometheus-server:9090'
NAMESPACE = 'your-namespace'

def list_pod_resources():
    with grpc.insecure_channel('unix:///var/lib/kubelet/pod-resources/kubelet.sock') as channel:
        stub = api_pb2_grpc.PodResourcesListerStub(channel)
        response = stub.List(api_pb2.ListPodResourcesRequest())
        pod_resources = []
        for pod in response.pod_resources:
            pod_info = {
                "name": pod.name,
                "namespace": pod.namespace,
                "containers": []
            }
            for container in pod.containers:
                container_info = {
                    "name": container.name,
                    "devices": []
                }
                for device in container.devices:
                    container_info["devices"].append({
                        "resource_name": device.resource_name,
                        "device_ids": device.device_ids
                    })
                pod_info["containers"].append(container_info)
            pod_resources.append(pod_info)
    return pod_resources

def query_prometheus(query):
    response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={'query': query})
    response.raise_for_status()
    return response.json()['data']['result']

def filter_gpu_metrics_by_namespace(pod_resources, namespace):
    namespace_devices = set()
    for pod in pod_resources:
        if pod['namespace'] == namespace:
            for container in pod['containers']:
                for device in container['devices']:
                    namespace_devices.update(device['device_ids'])
    metrics = query_prometheus('DCGM_FI_DEV_GPU_UTIL')
    namespace_metrics = []
    for metric in metrics:
        if metric['metric'].get('UUID') in namespace_devices:
            namespace_metrics.append(metric)
    return namespace_metrics

def main():
    pod_resources = list_pod_resources()
    namespace_metrics = filter_gpu_metrics_by_namespace(pod_resources, NAMESPACE)
    print(namespace_metrics)

if __name__ == '__main__':
    main()
```

## This README provides a comprehensive guide on setting up and running the GPU usage billing script. If you have any questions or need further assistance, feel free to reach out.

### Take a look at following repos for more gpu monitoring examples:
- https://github.com/nawafalageel/docker_container_gpu_exporter.git
- https://github.com/dashpole/example-gpu-monitor.git 
