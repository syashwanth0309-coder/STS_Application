import socket
import pickle
import hashlib

from utility_auth import verify_user
from utility_RSA import generate_key_pair, encrypt, decrypt, deserialize_public_key, serialize_public_key


def get_sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


users = {
    "kili": get_sha256("yash@143"),
    "admin": get_sha256("admin@1234"),
    "buddy": get_sha256("buddy@1234")
}


def server_program():
    server_private, server_public = generate_key_pair()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 12345))   # listen on all interfaces
    s.listen(1)
    print("Server listening on port 12345...")
    conn, addr = s.accept()
    print("Client connected:", addr)

    # Login phase
    conn.send(pickle.dumps("Enter the username : "))
    username = pickle.loads(conn.recv(4096))
    conn.send(pickle.dumps("Enter the password : "))
    password = pickle.loads(conn.recv(4096))

    if verify_user(username, password):
        conn.send(pickle.dumps(f"Login successful! Welcome {username}"))
        print(f"User {username} logged in.")
    else:
        conn.send(pickle.dumps("Login failed, connection closed"))
        conn.close()
        s.close()
        return

    # Exchange public keys
    conn.send(pickle.dumps(serialize_public_key(server_public)))
    client_public_pem = pickle.loads(conn.recv(4096))
    client_public = deserialize_public_key(client_public_pem)

    while True:
        enc_msg = pickle.loads(conn.recv(4096))
        dec_msg = decrypt(enc_msg, server_private)
        if dec_msg.lower() == "exit":
            print("Client disconnected.")
            break
        print(f"{username}: {dec_msg}")

        reply = input("Server: ")
        enc_reply = encrypt(reply, client_public)
        conn.send(pickle.dumps(enc_reply))

    conn.close()
    s.close()


if __name__ == "__main__":
    server_program()
