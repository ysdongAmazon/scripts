Envoy Version Update Script for AWS ECS
---------------------------------------

This Python script updates the Envoy version for all services in a specified Amazon Elastic Container Service (ECS) cluster. The script replaces the existing Envoy image version with the desired version and performs a rolling update of the ECS services.  
It could be used to migrate services from a less compatible envoy version faster. (App Mesh will stop supporting versions before 1.17 in the future)  
Ref: https://docs.aws.amazon.com/app-mesh/latest/userguide/envoy.html

Prerequisites
-------------

Before running this script, ensure you have the following installed/Set up:

- Python 3
- Boto3 (AWS SDK for Python)
- Set up your AWS credentials and default region

Usage
-----
```
python3 updateECSEnvoyVersion.py <cluster_name> <envoy_image_version>
```

Replace `<cluster_name>` with the name of your ECS cluster.  
Replace `<envoy_image_version>` with the desired Envoy image version.

Available envoy version: https://gallery.ecr.aws/appmesh/aws-appmesh-envoy

How the script works
--------------------

The script performs the following steps:

1. Lists all services in the specified ECS cluster.
2. Describes each service to get the current task definition.
3. Checks if the task definition contains an Envoy container.
4. If an Envoy container is found, creates a new task definition with the desired Envoy image version.
5. Updates the service with the new task definition using a rolling update strategy.
6. Monitors the update progress and prints the status of each service.

Limitations
-------------------------------

1. The script assumes that all tasks in a service are replicas use the same task definition.
2. Ensure that you have appropriate permissions to list, describe, and update ECS services and task definitions.
3. For services with only a single task (replica), please consider the short outrage caused by the update.
4. Consider implementing additional error handling, rate limiting, and monitoring for more robust and reliable updates.
