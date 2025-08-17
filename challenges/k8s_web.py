"""
k8s_web

Defines the challenge type for web challenges.
"""

from flask import Blueprint # pylint: disable=import-error
from .k8s_challenge import K8sChallengeType

class K8sWebChallengeType(K8sChallengeType):
    """
    The challenge type for web challenges.
    """
    id = "k8s-web"
    name = "k8s-web"
    templates = {
        "create": "ctfd-templates/k8s_web/create.html",
        "update": "ctfd-templates/k8s_web/update.html",
        "view": "ctfd-templates/k8s_web/view.html",
    }
    scripts = {
        "create": "k8s_web/create.js",
        "update": "k8s_web/update.js",
        "view": "k8s_web/view.js",
    }
    route = '/plugins/ctfd-k8s-challenge/assets/k8s_web'
    blueprint = Blueprint(
        "ctfd-k8s-challenge",
        __name__,
        template_folder="ctfd-templates",
        static_folder="assets"
    )
