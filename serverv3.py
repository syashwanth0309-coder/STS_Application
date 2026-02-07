import socket
import pickle
import hashlib
import threading
from utility_auth import verify_user
from utility_RSA import generate_key_pair, encrypt, decrypt, deserialize_public_key, serialize_public_key
from utility_network import broadcast_message


def get_sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


MAX_CLIENTS = 3
active_clients = {}
client_lock = threading.Lock()
next_user_index = 1


def handle_client(conn, addr):
    username = None
    display_name = None
    server_private, server_public = generate_key_pair()

    try:
        print(f"Client Requesting: {addr}")

        # Login phase
        username = pickle.loads(conn.recv(4096))
        password = pickle.loads(conn.recv(4096))

        # CHECKS DUPLICATE USERNAME FIRST
        with client_lock:
            if username in active_clients:
                conn.send(pickle.dumps(f"User '{username}' already online!"))
                print(f"Duplicate login attempt for {username} from {addr}")
                return

        if verify_user(username, password):
            global next_user_index
            display_name = f"Peer{next_user_index}"
            next_user_index += 1

            conn.send(pickle.dumps(
                f"Login successful! Welcome {username} (Your ID: {display_name})"))
            print(f"User {username} ({display_name}) logged in from {addr}")
        else:
            conn.send(pickle.dumps("Login failed, connection closed"))
            return

        # Exchange public keys
        conn.send(pickle.dumps(serialize_public_key(server_public)))
        client_public_pem = pickle.loads(conn.recv(4096))
        client_public = deserialize_public_key(client_public_pem)

        # Store active client
        with client_lock:
            active_clients[username] = {
                'display_name': display_name,
                'conn': conn,
                'public_key': client_public,
                'server_private': server_private,
                'addr': addr
            }
            print(
                f"Active clients: {len(active_clients)}/{MAX_CLIENTS} | Users: {[data['display_name'] for data in active_clients.values()]}")

        # FULL DUPLEX receive thread
        def receive_thread():
            while username in active_clients:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    enc_msg = pickle.loads(data)
                    dec_msg = decrypt(enc_msg, server_private)

                    if dec_msg.lower() == "exit":
                        print(f"{display_name} ({username}) disconnected")
                        break

                    print(f"{username} ({addr}): {dec_msg}")

                    # Handle client broadcast format: "Peer1|message"
                    if '|' in dec_msg:
                        sender_display, message = dec_msg.split('|', 1)
                        broadcast_message(
                            active_clients, client_lock, sender_display, username, message)
                    else:
                        # Regular message - just log
                        print(f"LOG [{display_name} ({username})]: {dec_msg}")

                except:
                    break

        recv_thread = threading.Thread(target=receive_thread, daemon=True)
        recv_thread.start()

        # Server send loop - broadcasts to ALL
        while username in active_clients:
            try:
                reply = input()
                if reply.lower() == "exit":
                    break
                broadcast_message(active_clients, client_lock,
                                  "MAIN", "SERVER", reply)
            except KeyboardInterrupt:
                break

    except Exception as e:
        print(f"Error with {username} ({display_name}): {e}")
    finally:
        with client_lock:
            if username in active_clients:
                del active_clients[username]
        if conn:
            conn.close()
        print(
            f"Client {display_name} ({username}) disconnected. Active: {len(active_clients)}")


def server_program():
    global next_user_index
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 12345))
    s.listen(MAX_CLIENTS)
    print(f"Server listening on port 12345 (MAX {MAX_CLIENTS} unique clients)")
    print("Users will be assigned: Peer1, Peer2, Peer3 by connection order")

    while True:
        try:
            conn, addr = s.accept()
            if len(active_clients) >= MAX_CLIENTS:
                print("Max clients reached!")
                conn.send(pickle.dumps("Server full - max 3 clients"))
                conn.close()
                continue

            client_thread = threading.Thread(
                target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            break

    s.close()


if __name__ == "__main__":
    server_program()
