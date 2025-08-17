"""
challenges

This module implements the actual challenge types of the plugins.
"""
import re
import uuid
import hashlib
import bcrypt
from CTFd.models import db, Challenges                                               # pylint: disable=import-error
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES, get_chal_class # pylint: disable=import-error

from .k8s_tcp import *
from .k8s_web import *
from .k8s_random_port import *
from .k8s_admin import define_k8s_admin
from ..utils import *

def init_chals(k8s_client):
    """
    Initializes resources for the challenge types.
    Also registers the actual challenge classes.
    """
    config = get_config()
    print(f"ctfd-k8s-challenge: Debug - challenge_namespace: {config.challenge_namespace}")

    if not config.challenge_namespace:
        print("ctfd-k8s-challenge: Debug - No challenge_namespace configured, returning False")
        return False

    print("ctfd-k8s-challenge: Debug - Starting deployment of core resources...")
    
    result = deploy_certificates(k8s_client, config)
    print(f"ctfd-k8s-challenge: Debug - deploy_certificates result: {result}")
    
    result = False if not result else deploy_web_gateway(k8s_client, config)
    print(f"ctfd-k8s-challenge: Debug - deploy_web_gateway result: {result}")
    
    # Skip registry deployment since we're using external registry.psuccso.org
    # result = False if not result else deploy_registry(k8s_client, config)
    
    result = False if not result else deploy_cleanup_cronjob(k8s_client, config)
    print(f"ctfd-k8s-challenge: Debug - deploy_cleanup_cronjob result: {result}")

    if result:
        print("ctfd-k8s-challenge: Debug - All resources deployed successfully, registering challenge classes...")
        CHALLENGE_CLASSES['k8s-tcp'] = K8sTcpChallengeType
        CHALLENGE_CLASSES['k8s-web'] = K8sWebChallengeType
        CHALLENGE_CLASSES['k8s-random-port'] = K8sRandomPortChallengeType
        print("ctfd-k8s-challenge: Debug - Challenge classes registered successfully")
    else:
        print("ctfd-k8s-challenge: Debug - Resource deployment failed, not registering challenge classes")

    return result

def deinit_chals(k8s_client):
    """
    Removes challenge resources.

    Currently unused.
    """

    config = get_config()

    result = destroy_certificates(k8s_client, config)
    result = False if not result else destroy_cleanup_cronjob(k8s_client, config)
    result = False if not result else destroy_web_gateway(k8s_client, config)
    # Skip registry destruction since we're using external registry.psuccso.org
    # result = False if not result else destroy_registry(k8s_client, config)

    return result

def deploy_registry(k8s_client, config):
    """
    Deploys the internal challenge registry in Kubernetes.
    """

    def encrypt_password(username, password):
        """
        Quick function to return a htpasswd formatted hash of password.
        """

        bcrypted = bcrypt.hashpw(password.encode("utf-8"),
                                bcrypt.gensalt(rounds=12)).decode("utf-8")
        bcrypted = re.sub(r"\$2[^a]\$", "$2y$", bcrypted)
        return f"{username}:{bcrypted}"

    result = False
    template = get_template('registry')

    if not config.registry_password:
        config.registry_password = str(hashlib.md5(bytes(str(uuid.uuid4()), 'utf-8')).hexdigest())
        db.session.commit()

    registry_hash = encrypt_password('ctfd', config.registry_password)

    options = {'registry_namespace': config.registry_namespace,
               'https_domain_name': config.https_domain_name,
               'registry_hash': registry_hash}

    if deploy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully deployed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: deploying k8s internal challenge registry failed!")
    return result

def deploy_certificates(k8s_client, config):
    """
    Deploys the certificates for the challenge endpoints.
    Note: With nginx-ingress, certificates are handled automatically.
    """

    result = True  # No need to deploy separate certificates with nginx-ingress
    print("ctfd-k8s-challenge: Certificates not needed with nginx-ingress.")
    return result

def deploy_web_gateway(k8s_client, config):
    """
    Deploys the web gateway for the web challenges.
    Note: With nginx-ingress, this is handled by individual challenge ingress resources.
    """

    result = True  # No need to deploy separate gateway with nginx-ingress
    print("ctfd-k8s-challenge: Web gateway not needed with nginx-ingress.")
    return result

def deploy_cleanup_cronjob(k8s_client, config):
    """
    Deploys the cronjob which calls the /api/v1/k8s/clean endpoint every minute.
    Note: This is optional and won't prevent the plugin from initializing.
    """

    print(f"ctfd-k8s-challenge: Debug - Deploying cleanup cronjob to namespace: {config.challenge_namespace}")
    print(f"ctfd-k8s-challenge: Debug - CTFd URL: {config.ctfd_url}")
    
    try:
        result = False
        template = get_template('clean')
        print(f"ctfd-k8s-challenge: Debug - Got template: {template is not None}")
        
        options = {'ctfd_url': config.ctfd_url,
                   'challenge_namespace': config.challenge_namespace}
        print(f"ctfd-k8s-challenge: Debug - Template options: {options}")
        
        if deploy_object(k8s_client, template, options):
            result = True
            print("ctfd-k8s-challenge: Successfully deployed cleanup cronjob.")
        else:
            print("ctfd-k8s-challenge: Warning: deploying cleanup cronjob failed, but continuing...")
            result = True  # Don't fail the entire initialization
            
    except Exception as e:
        print(f"ctfd-k8s-challenge: Warning: cleanup cronjob deployment failed with error: {e}")
        print("ctfd-k8s-challenge: Continuing initialization without cleanup cronjob...")
        result = True  # Don't fail the entire initialization
    
    print(f"ctfd-k8s-challenge: Debug - deploy_cleanup_cronjob returning: {result}")
    return result

def destroy_registry(k8s_client, config):
    """
    Destroys the registry deployment from Kubernetes.
    """

    result = False
    template = get_template('registry')
    options = {'registry_namespace': config.registry_namespace}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed k8s internal challenge registry.")
    else:
        print("ctfd-k8s-challenge: Error: destroying k8s internal challenge registry failed!")
    return result

def destroy_certificates(k8s_client, config):
    """
    Destroys the certificates from Kubernetes.
    Note: With nginx-ingress, certificates are handled automatically.
    """

    result = True  # No need to destroy separate certificates with nginx-ingress
    print("ctfd-k8s-challenge: Certificates not managed separately with nginx-ingress.")
    return result

def destroy_web_gateway(k8s_client, config):
    """
    Destroys the web gateway from Kubernetes.
    Note: With nginx-ingress, this is handled by individual challenge ingress resources.
    """

    result = True  # No need to destroy separate gateway with nginx-ingress
    print("ctfd-k8s-challenge: Web gateway not managed separately with nginx-ingress.")
    return result

def destroy_cleanup_cronjob(k8s_client, config):
    """
    Destroys the cleanup cronjob.
    """

    result = False
    template = get_template('clean')
    options = {'ctfd_url': config.ctfd_url,
               'challenge_namespace': config.challenge_namespace}
    if destroy_object(k8s_client, template, options):
        result = True
        print("ctfd-k8s-challenge: Successfully destroyed cleanup cronjob.")
    else:
        print("ctfd-k8s-challenge: Error: destroying cleanup cronjob failed!")
    return result
