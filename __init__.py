# pylint: disable=invalid-name
"""
CTFd-K8s-Challenges

This plugin enables CTFd to create
containerized challenge instances using Kubernetes.
"""

import os
import sys
from CTFd.plugins import register_plugin_assets_directory  # pylint: disable=import-error

from .challenges import init_chals, deinit_chals, define_k8s_admin
from .utils import init_db, get_k8s_client, define_k8s_api

# Import challenge models so they are registered with SQLAlchemy
from .challenges.k8s_challenge import (
    K8sChallenge,
    K8sTcpChallenge,
    K8sWebChallenge,
    K8sRandomPortChallenge,
)


def load(app):
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    # Add ctfd-templates to Python path
    ctfd_templates_dir = os.path.join(plugin_dir, 'ctfd-templates')
    if ctfd_templates_dir not in sys.path:
        sys.path.insert(0, ctfd_templates_dir)

    # Create database tables
    app.db.create_all()

    # Initialize Kubernetes client
    k8s_client = get_k8s_client()
    print("ctfd-k8s-challenge: Successfully loaded Kubernetes config.")

    # Initialize plugin DB and admin settings
    init_db()
    define_k8s_admin(app)

    try:
        if init_chals(k8s_client):
            # Correctly register plugin assets
            register_plugin_assets_directory(
                app,
                base_path='/plugins/ctfd-k8s-challenge/assets'
            )
            # Define Kubernetes API routes
            define_k8s_api(app)
        else:
            print("ctfd-k8s-challenge: Error initializing challenges. Plugin disabled.")
    except Exception as e:
        print("CTFd-K8S PLUGIN INIT ERROR:", e)
        raise
