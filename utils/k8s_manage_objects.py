"""
k8s_manage_objects

The code where objects are templated from yaml and deployed to k8s.
"""

import yaml
from jinja2 import Template
import kubernetes as k8s

from .k8s_delete_from_yaml import delete_from_yaml
from .k8s_manage_custom_resources import (apply_custom_object_from_yaml,
                                          delete_custom_object_from_yaml)

def get_template(template_name):
    """
    Returns the template yaml from the name.
    """
    template_path = 'CTFd/plugins/ctfd-k8s-challenge/templates/' + template_name + '.yml.j2'

    template = ''

    with open(template_path, encoding='utf-8') as t_file:
        template = t_file.read()

    return Template(template)


def deploy_object(k8s_client, template, template_variables):
    """
    Deploys the object to kubernetes.
    """
    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    for yaml_file in dep:
        api_name = yaml_file['apiVersion']
        kind = yaml_file['kind']

        if 'cert-manager' in api_name or 'istio' in api_name or kind == 'Job':
            apply_custom_object_from_yaml(k8s_client, yaml_file)
        else:
            try:
                k8s.utils.create_from_yaml(k8s_client, yaml_objects=[yaml_file])
            except Exception as general_exception: # pylint: disable=broad-except
                if '"reason":"AlreadyExists"' not in str(general_exception):
                    result = False
                    print("ERROR: ctfd-k8s-challenges: ", general_exception)

    return result


def destroy_object(k8s_client, template, template_variables):
    """
    Destroys the given object from kubernetes.
    """
    spec = template.render(template_variables)

    dep = yaml.safe_load_all(spec)

    result = True

    for yaml_file in dep:
        api_name = yaml_file['apiVersion']
        kind = yaml_file['kind']

        if 'cert-manager' in api_name or 'istio' in api_name or kind == 'Job':
            delete_custom_object_from_yaml(k8s_client, yaml_file)
        else:
            try:
                delete_from_yaml(k8s_client, yaml_objects=[yaml_file])
            except Exception as general_exception: # pylint: disable=broad-except
                result = False
                print("ERROR: ctfd-k8s-challenges: ", general_exception)
    return result

def add_ingress_port(k8s_client, config, port):
    """
    With nginx-ingress, ports are handled automatically by the ingress controller.
    This function is kept for compatibility but does nothing.
    """
    result = True
    print("ctfd-k8s-challenges: Port management not needed with nginx-ingress")
    return result

def delete_ingress_port(k8s_client, config, port):
    """
    With nginx-ingress, ports are handled automatically by the ingress controller.
    This function is kept for compatibility but does nothing.
    """
    result = True
    print("ctfd-k8s-challenges: Port management not needed with nginx-ingress")
    return result
