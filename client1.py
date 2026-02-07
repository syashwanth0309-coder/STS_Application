import socket
import pickle
import threading
from utility_RSA import generate_key_pair, encrypt, decrypt, deserialize_public_key, serialize_public_key


def client_program():
    client_private, client_public = generate_key_pair()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    print("Connected to server...")

    # Login phase
    username = input("Username: ")
    s.send(pickle.dumps(username))
    password = input("Password: ")
    s.send(pickle.dumps(password))
    login_msg = pickle.loads(s.recv(4096))
    print(login_msg)

    if "failed" in login_msg.lower():
        print("Login failed")
        s.close()
        return

    # Extract display_name from login message
    display_name = login_msg.split("ID: ")[-1].strip(")")
    print(f"Your display name: {display_name}")

    # Exchange public keys
    s.send(pickle.dumps(serialize_public_key(client_public)))
    server_public_pem = pickle.loads(s.recv(4096))
    server_public = deserialize_public_key(server_public_pem)

    print("Encryption enabled. Type 'exit' to quit.")
    print("Messages from other clients will appear here...\n")

    # FULL DUPLEX: Separate receive thread
    def receive_thread():
        while True:
            try:
                data = s.recv(4096)
                if not data:
                    break
                enc_msg = pickle.loads(data)
                dec_msg = decrypt(enc_msg, client_private)
                if dec_msg.lower() == "exit":
                    print("\nServer disconnected you.")
                    break
                print(f"{dec_msg}\n", end="")
            except:
                print("\nConnection lost.")
                break
        s.close()
        print("Disconnected.")

    recv_thread = threading.Thread(target=receive_thread, daemon=True)
    recv_thread.start()

    # Send loop - broadcasts using display_name
    try:
        while True:
            reply = input()
            if reply.lower() == "exit":
                enc_reply = encrypt(reply, server_public)
                s.send(pickle.dumps(enc_reply))
                break
            # Send message with display_name prefix for server broadcast
            broadcast_msg = f"{display_name}|{reply}"
            enc_reply = encrypt(broadcast_msg, server_public)
            s.send(pickle.dumps(enc_reply))
    except KeyboardInterrupt:
        print("\nGoodbye!")

    s.close()


if __name__ == "__main__":
    client_program()
# broadcast_message