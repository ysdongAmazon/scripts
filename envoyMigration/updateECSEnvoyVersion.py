import boto3
import sys
import time
import threading
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

def list_services(ecs, cluster_name):
    service_arns = []
    paginator = ecs.get_paginator('list_services')
    for page in paginator.paginate(cluster=cluster_name):
        service_arns.extend(page['serviceArns'])
    return service_arns

def upgrade_envoy_image(task_definition, envoy_image_version):
    container_definitions = task_definition['containerDefinitions']
    updated = False
    # e.g. "public.ecr.aws/appmesh/aws-appmesh-envoy:v1.24.2.0-prod"
    new_envoy_version = "public.ecr.aws/appmesh/aws-appmesh-envoy:v" + envoy_image_version + "-prod"

    for container_definition in container_definitions:
            if 'envoy' in container_definition['name'].lower():
                container_definition['image'] = new_envoy_version
                updated = True

    return updated, container_definitions

def monitor_update_deployment(cluster_name, service_arn, ecs, timeout=3600):
    start_time = time.time()

    while True:
        time.sleep(10)
        service = ecs.describe_services(cluster=cluster_name, services=[service_arn])['services'][0]
        deployments = service['deployments']
        primary_deployment = None
        for deployment in deployments:
            if deployment['status'] == 'PRIMARY':
                primary_deployment = deployment
                break
        
        if primary_deployment['desiredCount'] == primary_deployment['runningCount']:
            # new tasks are running as expected
            if primary_deployment['rolloutState'] == 'COMPLETED':
                logging.info(f"Service {service['serviceName']} is updated successfully")
                break
            elif primary_deployment['rolloutState'] == 'FAILED':
                logging.error(f"Deployment failed for service {service['serviceName']}, \
                rolloutState: {primary_deployment['rolloutState']}, \
                rolloutReason: {primary_deployment['rolloutStateReason']}")
                break
            else:
                logging.info(f"Service {service['serviceName']} is still updating...")
        elif primary_deployment['failedTasks'] > 0:
            logging.error(f"Deployment failed with failedTasks for service {service['serviceName']}, \
            rolloutState: {primary_deployment['rolloutState']}, \
            rolloutReason: {primary_deployment['rolloutStateReason']}")
            break
        else:
            logging.info(f"Service {service['serviceName']} is still updating...")

        if time.time() - start_time > timeout:
            logging.warning(f"Monitoring timed out for service {service['serviceName']}")
            break

def main():
    if len(sys.argv) != 3:
        logging.error(f"Usage: python {sys.argv[0]} <cluster_name> <envoy_image_version>")
        sys.exit(1)
    cluster_name = sys.argv[1]
    envoy_image_version = sys.argv[2]
    if not cluster_name or not envoy_image_version:
        logging.error(f"Cluster_name and envoy_image_version can not be empty")
        sys.exit(1)

    ecs = boto3.client('ecs')
    try:
        service_arn_list = list_services(ecs, cluster_name)
    except ClientError as e:
        logging.error(f"Error listing services in cluster {cluster_name}: {e}")
        sys.exit(1)

    monitor_threads = []

    for service_arn in service_arn_list:
        service = ecs.describe_services(cluster=cluster_name, services=[service_arn])['services'][0]
        task_definition_arn = service['taskDefinition']
        task_definition = ecs.describe_task_definition(taskDefinition=task_definition_arn)['taskDefinition']

        updated, container_definitions = upgrade_envoy_image(task_definition, envoy_image_version)
        
        if updated:
            exclude_keys = ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'compatibilities', 'registeredAt', 'registeredBy']
            new_task_definition_data ={
                key: value for key, value in task_definition.items() if key not in exclude_keys
            }
            new_task_definition_data['containerDefinitions'] = container_definitions

            new_task_definition = ecs.register_task_definition(
                **new_task_definition_data
            )

            new_task_definition_arn = new_task_definition['taskDefinition']['taskDefinitionArn']
            
            # By default, update service would use rolling deployment type
            ecs.update_service(
                cluster=cluster_name,
                service=service_arn,
                taskDefinition=new_task_definition_arn,
                deploymentConfiguration={
                    'deploymentCircuitBreaker': {
                        'enable': True,
                        'rollback': True
                    },
                    'maximumPercent': 200,
                    # 'minimumHealthyPercent': 50 
                }
            )
            monitor_thread = threading.Thread(target=monitor_update_deployment, args=(cluster_name, service_arn, ecs))
            monitor_threads.append(monitor_thread)
            monitor_thread.start()
        else:
            print(f"No Envoy image found in service {service['serviceName']}")
        
    for monitor_thread in monitor_threads:
        monitor_thread.join()

if __name__ == '__main__':
    main()