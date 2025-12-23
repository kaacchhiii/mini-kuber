import kopf
import kubernetes
import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_deployment_manifest(name: str, namespace: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": {
                "app": name,
                "managed-by": "simpleweb-operator"
            }
        },
        "spec": {
            "replicas": spec.get("replicas", 1),
            "selector": {
                "matchLabels": {
                    "app": name
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": name
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": spec.get("image"),
                            "ports": [
                                {
                                    "containerPort": spec.get("port"),
                                    "name": "http"
                                }
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "64Mi",
                                    "cpu": "50m"
                                },
                                "limits": {
                                    "memory": "128Mi",
                                    "cpu": "100m"
                                }
                            }
                        }
                    ]
                }
            }
        }
    }


def create_service_manifest(name: str, namespace: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": {
                "app": name,
                "managed-by": "simpleweb-operator"
            }
        },
        "spec": {
            "type": "ClusterIP",
            "selector": {
                "app": name
            },
            "ports": [
                {
                    "port": spec.get("port"),
                    "targetPort": spec.get("port"),
                    "protocol": "TCP",
                    "name": "http"
                }
            ]
        }
    }


@kopf.on.create('ops.example.com', 'v1', 'simplewebs')
def create_fn(spec, name, namespace, logger, body, **kwargs):
    logger.info(f"Creating resources for SimpleWeb '{name}' in namespace '{namespace}'")
    logger.info(f"Spec: image={spec.get('image')}, port={spec.get('port')}, replicas={spec.get('replicas')}")
    
    api = kubernetes.client.ApiClient()
    apps_v1 = kubernetes.client.AppsV1Api(api)
    core_v1 = kubernetes.client.CoreV1Api(api)
    
    deployment_manifest = create_deployment_manifest(name, namespace, spec)
    kopf.append_owner_reference(deployment_manifest, owner=body)
    
    try:
        deployment = apps_v1.create_namespaced_deployment(
            namespace=namespace,
            body=deployment_manifest
        )
        logger.info(f"✓ Created Deployment '{name}' with {spec.get('replicas')} replicas")
    except kubernetes.client.exceptions.ApiException as e:
        logger.error(f"✗ Failed to create Deployment: {e}")
        raise kopf.PermanentError(f"Failed to create Deployment: {e}")
    
    service_manifest = create_service_manifest(name, namespace, spec)
    kopf.append_owner_reference(service_manifest, owner=body)
    
    try:
        service = core_v1.create_namespaced_service(
            namespace=namespace,
            body=service_manifest
        )
        logger.info(f"✓ Created Service '{name}' on port {spec.get('port')}")
    except kubernetes.client.exceptions.ApiException as e:
        logger.error(f"✗ Failed to create Service: {e}")
        raise kopf.PermanentError(f"Failed to create Service: {e}")
    
    return {
        'deployment': deployment.metadata.name,
        'service': service.metadata.name,
        'message': f"Successfully created Deployment and Service for {name}"
    }


@kopf.on.update('ops.example.com', 'v1', 'simplewebs')
def update_fn(spec, name, namespace, old, new, diff, logger, **kwargs):
    logger.info(f"Updating resources for SimpleWeb '{name}' in namespace '{namespace}'")
    
    api = kubernetes.client.ApiClient()
    apps_v1 = kubernetes.client.AppsV1Api(api)
    
    changed_fields = [item[0] for item in diff]
    logger.info(f"Changed fields: {changed_fields}")
    
    patch = {}
    needs_patch = False
    
    if ('change', ('spec', 'replicas'), old['spec'].get('replicas'), new['spec'].get('replicas')) in diff:
        old_replicas = old['spec'].get('replicas')
        new_replicas = new['spec'].get('replicas')
        logger.info(f"Replicas changed: {old_replicas} → {new_replicas}")
        patch['spec'] = patch.get('spec', {})
        patch['spec']['replicas'] = new_replicas
        needs_patch = True
    
    if ('change', ('spec', 'image'), old['spec'].get('image'), new['spec'].get('image')) in diff:
        old_image = old['spec'].get('image')
        new_image = new['spec'].get('image')
        logger.info(f"Image changed: {old_image} → {new_image}")
        patch['spec'] = patch.get('spec', {})
        patch['spec']['template'] = {
            'spec': {
                'containers': [
                    {
                        'name': name,
                        'image': new_image
                    }
                ]
            }
        }
        needs_patch = True
    
    if ('change', ('spec', 'port'), old['spec'].get('port'), new['spec'].get('port')) in diff:
        old_port = old['spec'].get('port')
        new_port = new['spec'].get('port')
        logger.info(f"Port changed: {old_port} → {new_port}")
        logger.warning("Port changes require recreating the Service. Updating Deployment container port.")
        patch['spec'] = patch.get('spec', {})
        patch['spec']['template'] = patch['spec'].get('template', {})
        patch['spec']['template']['spec'] = patch['spec']['template'].get('spec', {})
        patch['spec']['template']['spec']['containers'] = [
            {
                'name': name,
                'ports': [
                    {
                        'containerPort': new_port,
                        'name': 'http'
                    }
                ]
            }
        ]
        needs_patch = True
    
    if needs_patch:
        try:
            apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=patch
            )
            logger.info(f"✓ Successfully patched Deployment '{name}'")
        except kubernetes.client.exceptions.ApiException as e:
            logger.error(f"✗ Failed to patch Deployment: {e}")
            raise kopf.PermanentError(f"Failed to patch Deployment: {e}")
    else:
        logger.info("No actionable changes detected")
    
    return {'message': f"Successfully updated {name}"}


@kopf.on.delete('ops.example.com', 'v1', 'simplewebs')
def delete_fn(spec, name, namespace, logger, **kwargs):
    logger.info(f"SimpleWeb '{name}' in namespace '{namespace}' is being deleted")
    logger.info("Kubernetes will automatically delete child resources (Deployment, Service) via owner references")
    
    return {'message': f"SimpleWeb {name} deleted. Child resources will be garbage collected."}


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.persistence.finalizer = 'simplewebs.ops.example.com/finalizer'
    settings.posting.enabled = True
    settings.posting.level = logging.INFO
    
    logger.info("SimpleWeb Operator started successfully")
    logger.info("Watching for SimpleWeb resources in all namespaces")
