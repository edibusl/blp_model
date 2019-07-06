import hashlib, uuid


def pass_to_hash(password, salt=None):
    if not password:
        raise ValueError("Empty password given")

    if not salt:
        salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((password + salt).encode('ascii')).hexdigest()

    return hashed_password, salt
