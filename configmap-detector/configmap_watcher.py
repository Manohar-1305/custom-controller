from kubernetes import client, config, watch
import time

# Load Kubernetes config (inside cluster or local)
try:
    config.load_incluster_config()
except config.config_exception.ConfigException:
    config.load_kube_config()

api = client.CoreV1Api()
apps_api = client.AppsV1Api()
crd_api = client.CustomObjectsApi()

NAMESPACE = "default"

def restart_deployment(deployment_name):
    """Patch the deployment to trigger a restart."""
    try:
        deployment = apps_api.read_namespaced_deployment(deployment_name, NAMESPACE)
        if "annotations" not in deployment.spec.template.metadata:
            deployment.spec.template.metadata.annotations = {}
        deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = str(time.time())
        apps_api.patch_namespaced_deployment(deployment_name, NAMESPACE, deployment)
        print(f"Restarted deployment: {deployment_name}")
    except Exception as e:
        print(f"Failed to restart deployment {deployment_name}: {e}")

def watch_configmap_changes():
    """Watch for ConfigMap changes and restart deployments accordingly."""
    w = watch.Watch()
    for event in w.stream(api.list_namespaced_config_map, namespace=NAMESPACE):
        cm_name = event["object"].metadata.name
        event_type = event["type"]
        print(f"Event: {event_type} on ConfigMap {cm_name}")

        # Check if a CRD instance is watching this ConfigMap
        try:
            cr_list = crd_api.list_namespaced_custom_object(
                group="configmapwatchers.io", version="v1", namespace=NAMESPACE, plural="configmapwatchers"
            )
            for cr in cr_list.get("items", []):
                if cr["spec"]["configMapName"] == cm_name:
                    restart_deployment(cr["spec"]["deploymentName"])
        except Exception as e:
            print(f"Failed to check CRD instances: {e}")

if __name__ == "__main__":
    print("Starting ConfigMap watcher...")
    watch_configmap_changes()
