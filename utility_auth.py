import hashlib

users = {
    "Yash": hashlib.sha256("yash@1234".encode()).hexdigest(),
    "admin": hashlib.sha256("admin@1234".encode()).hexdigest(),
    "buddy": hashlib.sha256("buddy@1234".encode()).hexdigest()
}


def verify_user(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return users.get(username) == hashed
