"""
k8s_database

Creates wrapper functions around most database operations.
"""

from math import floor
from datetime import datetime

from CTFd.models import db, Challenges, Users # pylint: disable=import-error
from CTFd.utils.dates import unix_time        # pylint: disable=import-error
from sqlalchemy import text, inspect          # pylint: disable=import-error


from .k8s_config import read_config_file

def init_db():
    """
    Initializes the database by trying to read the configuration file.
    """

    existing_config = K8sConfig.query.filter_by(id=1).first()
    if not existing_config:
        print("ctfd-k8s-challenge: Creating blank config.")
        existing_config = K8sConfig()
    file_config = read_config_file()
    if file_config:
        print("ctfd-k8s-challenge: Reading config from file.")
        columns = [column.name for column in inspect(K8sConfig).c]
        for column in columns:
            if column in file_config and getattr(existing_config, column) != file_config[column]:
                setattr(existing_config, column, file_config[column])
    db.session.add(existing_config)
    db.session.commit()


def get_config():
    """
    Returns the config dictionary.
    """
    return K8sConfig.query.filter_by(id=1).first()

def get_expired_challenges():
    """
    Returns a list of expired challenge objects.
    """
    expire_time = int(unix_time(datetime.utcnow()))
    query_str = 'revert_time<' + str(expire_time)
    return K8sChallengeTracker.query.filter(text(query_str)).order_by(text('revert_time')).all()

def extend_challenge_time(challenge):
    """
    Extends the challenge time by half the time if the challenge is eligible for extension.
    """
    extended = False
    config = get_config()
    if challenge.revert_time - unix_time(datetime.utcnow()) < config.expire_interval/2 and (
       challenge.revert_time - unix_time(datetime.utcnow()) > 0):
        challenge.revert_time = challenge.revert_time + floor(config.expire_interval/2)
        db.session.add(challenge)
        db.session.commit()
        extended = True
    return extended

def get_challenge_tracker():
    """
    Returns a list of all challenges in the tracker.
    """
    return K8sChallengeTracker.query.all()

def get_challenge_from_tracker(current_user_id):
    """
    Returns a user's current challenge from the tracker.
    """
    expire_time = int(unix_time(datetime.utcnow()))
    query_str = 'revert_time>' + str(expire_time)
    return K8sChallengeTracker.query.filter_by(
        user_id=current_user_id).filter(text(query_str)).order_by(text('revert_time')).first()

def get_all_challenges():
    """
    Returns a list of all challenges with proper names and users for the admin page.
    """
    challenges = []

    tracker = get_challenge_tracker()

    for chal in tracker:
        info = {
            'id': chal.challenge_id,
            'instance_id': chal.instance_id,
            'user_id': chal.user_id,
            'user': Users.query.filter_by(id=chal.user_id).first().name,
            'challenge_name': Challenges.query.filter_by(id=chal.challenge_id).first().name
        }
        challenges.append(info)

    return challenges

def insert_challenge_into_tracker(options, expire_time):
    """
    Inserts a new challenge into the tracker.
    """
    challenge = K8sChallengeTracker()
    challenge.chal_type = options['challenge_type']
    challenge.team_id = options['team']
    challenge.user_id = options['user']
    challenge.challenge_id = options['challenge_id']
    challenge.timestamp = unix_time(datetime.utcnow())
    challenge.revert_time = unix_time(datetime.utcnow()) + expire_time
    challenge.instance_id = options['instance_id']
    challenge.port = options['port']
    db.session.add(challenge)
    db.session.commit()

def remove_challenge_from_tracker(instance_id):
    """
    Removes a challenge from the tracker by the id.
    """
    K8sChallengeTracker.query.filter_by(id=instance_id).delete()
    db.session.commit()

def get_challenge_by_id(challenge_id):
    """
    Returns a specific challenge by its id.
    """
    return Challenges.query.filter_by(id=challenge_id).first()

def check_if_port_in_use(port):
    """
    Checks if a specific TCP port is being used.
    """
    available = False
    query = K8sChallengeTracker.query.filter_by(port=port).first()

    if not query:
        available = True

    return available

class K8sConfig(db.Model): #pylint: disable=too-few-public-methods
    """
	k8s Config Model. This model stores the config for the plugin.
	"""
    id = db.Column(db.Integer, primary_key=True)
    git_credential = db.Column("git_credential", db.String(256), index=False)
    git_user = db.Column("git_user", db.String(64), index=False)
    registry_password = db.Column("registry_password", db.String(64), index=False)
    registry_namespace = db.Column("registry_namespace", db.String(64), index=False)
    challenge_namespace = db.Column("challenge_namespace", db.String(64), index=False)
    # Removed istio_namespace and istio_ingress_name since we're using nginx-ingress
    tcp_domain_name = db.Column("tcp_domain_name", db.String(64), index=False)
    https_domain_name = db.Column("https_domain_name", db.String(64), index=False)
    # Removed certificate_issuer_name since nginx-ingress handles certs
    external_tcp_port = db.Column("external_tcp_port", db.Integer, index=False)
    external_https_port = db.Column("external_https_port", db.Integer, index=False)
    expire_interval = db.Column("expire_interval", db.Integer, index=False)
    ctfd_url = db.Column("ctfd_url", db.String(64), index=False)

class K8sChallengeTracker(db.Model): #pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
	K8s Container Tracker. This model stores the users/teams active containers.
	"""
    id = db.Column(db.Integer, primary_key=True)
    chal_type = db.Column("type", db.String(64), index=True)
    team_id = db.Column("team_id", db.String(64), index=True)
    user_id = db.Column("user_id", db.String(64), index=True)
    challenge_id = db.Column("challenge_id", db.Integer, index=True)
    timestamp = db.Column("timestamp", db.Integer, index=True)
    revert_time = db.Column("revert_time", db.Integer, index=True)
    instance_id = db.Column("instance_id", db.String(64), index=True)
    port = db.Column("port", db.Integer, index=True)
