import socket
import pickle

# from utility_auth import verify_user
from utility_RSA import generate_key_pair, encrypt, decrypt, deserialize_public_key, serialize_public_key


def client_program():
    client_private, client_public = generate_key_pair()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))   # replace with server IP
    print("Connected to server.")

    # Login phase
    print(pickle.loads(s.recv(4096)))
    username = input()
    s.send(pickle.dumps(username))
    print(pickle.loads(s.recv(4096)))
    password = input()
    s.send(pickle.dumps(password))
    print(pickle.loads(s.recv(4096)))

    # Exchange public keys
    s.send(pickle.dumps(serialize_public_key(client_public)))
    server_public_pem = pickle.loads(s.recv(4096))
    server_public = deserialize_public_key(server_public_pem)

    while True:
        reply = input("Client: ")
        enc_reply = encrypt(reply, server_public)
        s.send(pickle.dumps(enc_reply))
        if reply.lower() == "exit":
            break
        enc_msg = pickle.loads(s.recv(4096))
        dec_msg = decrypt(enc_msg, client_private)
        print("Server:", dec_msg)

    s.close()


if __name__ == "__main__":
    client_program()
