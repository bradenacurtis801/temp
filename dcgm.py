import grpc
import requests
import api_pb2
import api_pb2_grpc

PROMETHEUS_URL = 'http://10.10.231.2:9090'
NAMESPACE = 'foocus-api'

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
