import hashlib

users = {
    "kili": hashlib.sha256("yash@143".encode()).hexdigest(),
    "admin": hashlib.sha256("admin@1234".encode()).hexdigest(),
    "buddy": hashlib.sha256("buddy@1234".encode()).hexdigest()
}


def verify_user(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return users.get(username) == hashed
