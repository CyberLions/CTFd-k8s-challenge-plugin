# pylint: disable=invalid-name
"""
CTFd-K8s-Challenges

This plugin is built to enable CTFd to create
containerized challenge instances using Kubernetes.
"""

import os
import sys
from CTFd.plugins import register_plugin_assets_directory  # pylint: disable=import-error

from .challenges import init_chals, deinit_chals, define_k8s_admin
from .utils import init_db, get_k8s_client, define_k8s_api

# Import the K8sChallenge models so they are registered with SQLAlchemy
from .challenges.k8s_challenge import K8sChallenge, K8sTcpChallenge, K8sWebChallenge, K8sRandomPortChallenge

def load(app):
    """
    This function is called by CTFd to load the plugin.
    """
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    # Add ctfd-templates to Python path for template loading
    ctfd_templates_dir = os.path.join(plugin_dir, 'ctfd-templates')
    if ctfd_templates_dir not in sys.path:
        sys.path.insert(0, ctfd_templates_dir)

    # Initialize database and Kubernetes client
    app.db.create_all()
    k8s_client = get_k8s_client()
    print("ctfd-k8s-challenge: Successfully loaded Kubernetes config.")

    init_db()
    define_k8s_admin(app)

    try:
        if init_chals(k8s_client):
            # Register the plugin assets directory (JS/CSS files)
            assets_dir = os.path.join(plugin_dir, 'assets')
            register_plugin_assets_directory(
                app,
                base_path='/plugins/ctfd-k8s-challenge/assets',
                directory=assets_dir
            )

            define_k8s_api(app)
        else:
            print("ctfd-k8s-challenge: Error initializing challenges. Plugin disabled.")
    except Exception as e:
        print("CTFd-K8S PLUGIN INIT ERROR:", e)
        raise
