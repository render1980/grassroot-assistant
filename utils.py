import uuid
import hashlib


def generate_token(group, admin_id):
    print("generating token for group={} admin_id={}".format(group, admin_id))
    uid = uuid.uuid4()
    hash = hashlib.sha256("{}:{}:{}".format(group, admin_id, uid).encode("utf-8"))
    return hash.hexdigest()
