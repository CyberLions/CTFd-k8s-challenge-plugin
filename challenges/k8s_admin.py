"""
k8s_admin

This file defines the backend for the Admin interface for the plugin.
"""

import os
from flask import request, Blueprint, render_template
from CTFd.utils.decorators import admins_only         # pylint: disable=import-error
from CTFd.forms.fields import SubmitField             # pylint: disable=import-error
from CTFd.forms import BaseForm                       # pylint: disable=import-error
from CTFd.models import db                            # pylint: disable=import-error
from wtforms import HiddenField, PasswordField, StringField
from ..utils import get_config, get_all_challenges


class K8sConfigForm(BaseForm):  # pylint: disable=too-few-public-methods
    """
    This class defines the config form for the plugin.
    """

    id = HiddenField()
    git_credential = PasswordField(
        "Git Repository Credential",
        description="The secret used to access private Git repositories."
    )
    registry_namespace = StringField(
        "Registry Namespace",
        description="The namespace to deploy the internal container registry to."
    )
    challenge_namespace = StringField(
        "Challenge Namespace",
        description="The namespace to deploy challenges to."
    )
    istio_namespace = StringField(
        "Istio Namespace",
        description="The namespace where istio is deployed to."
    )
    tcp_domain_name = StringField(
        "TCP Domain Name",
        description="The domain name for TCP challenges."
    )
    https_domain_name = StringField(
        "Web Domain Name",
        description="The domain name for web challenges."
    )
    certificate_issuer_name = StringField(
        "Certificate Issuer Name",
        description="The name of the certificate issuer in the cluster."
    )
    istio_ingress_name = StringField(
        "Istio Ingress Name",
        description="The name of the cluster Istio Ingress Gateway."
    )
    external_tcp_port = StringField(
        "External TCP Port",
        description="The port that TCP/TLS challenges are exposed on."
    )
    external_https_port = StringField(
        "External Web Port",
        description="The port that web challenges are exposed on."
    )
    expire_interval = StringField(
        "Expire Interval",
        description="The time before a challenge instance expires in seconds."
    )
    ctfd_url = StringField(
        "CTFd URL",
        description="The URL that CTFd is accessible from within the cluster."
    )
    submit = SubmitField('Submit')


def define_k8s_admin(app):
    """
    Defines the actual route and backend for the admin web UI.
    """

    # Set plugin root directory (one level above 'challenges')
    plugin_root = os.path.dirname(os.path.dirname(__file__))

    # Register blueprint with absolute paths to templates and assets
    k8s_admin = Blueprint(
        'k8s_admin',
        __name__,
        template_folder=os.path.join(plugin_root, "templates"),
        static_folder=os.path.join(plugin_root, "assets")
    )

    @k8s_admin.route("/admin/kubernetes", methods=["GET", "POST"])
    @admins_only
    def admin():  # pylint: disable=too-many-branches
        config = get_config()
        form = K8sConfigForm()
        challenge_instances = []

        if request.method == "GET":
            challenge_instances = get_all_challenges()

        elif request.method == "POST":
            if len(request.form.get('git_credential', "")) > 0:
                config.git_credential = request.form['git_credential']
            config.registry_namespace = request.form['registry_namespace']
            config.challenge_namespace = request.form['challenge_namespace']
            config.istio_namespace = request.form['istio_namespace']
            config.tcp_domain_name = request.form['tcp_domain_name']
            config.https_domain_name = request.form['https_domain_name']
            config.certificate_issuer_name = request.form['certificate_issuer_name']
            config.istio_ingress_name = request.form['istio_ingress_name']
            config.external_tcp_port = int(request.form['external_tcp_port'])
            config.external_https_port = int(request.form['external_https_port'])
            config.expire_interval = int(request.form['expire_interval'])
            config.ctfd_url = request.form['ctfd_url']

            db.session.commit()

        return render_template(
            "ctfd-k8s-challenge/k8s_admin.html",
            config=config,
            form=form,
            challenge_instances=challenge_instances
        )

    # Register the blueprint with the main Flask app
    app.register_blueprint(k8s_admin)
