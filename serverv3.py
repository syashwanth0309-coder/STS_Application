import socket
import pickle
import hashlib
import threading
from utility_auth import verify_user
from utility_RSA import generate_key_pair, encrypt, decrypt, deserialize_public_key, serialize_public_key


def get_sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


MAX_CLIENTS = 3
active_clients = {}
client_lock = threading.Lock()
next_user_index = 1  # For u1, u2, u3 naming


def handle_client(conn, addr):
    """Handle single client connection - full duplex with unique users"""
    username = None
    display_name = None  # u1, u2, u3
    server_private, server_public = generate_key_pair()

    try:
        print(f"Client Requesting: {addr}")

        # Login phase
        # conn.send(pickle.dumps(""))
        username = pickle.loads(conn.recv(4096))
        # conn.send(pickle.dumps(""))
        password = pickle.loads(conn.recv(4096))

        # CHECKS DUPLICATE USERNAME FIRST
        with client_lock:
            if username in active_clients:
                conn.send(pickle.dumps(f"User '{username}' already online!"))
                print(f"Duplicate login attempt for {username} from {addr}")
                return

        if verify_user(username, password):
            # ASSIGN UNIQUE INDEX (u1, u2, u3)
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

        # Store active client with UNIQUE display_name
        with client_lock:
            active_clients[username] = {
                'display_name': display_name,  # u1, u2, u3
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
                    enc_msg = pickle.loads(conn.recv(4096))
                    dec_msg = decrypt(enc_msg, server_private)
                    if dec_msg.lower() == "exit":
                        print(f"{display_name} ({username}) disconnected")
                        break

                    print(f"{username} ({addr}): {dec_msg}")
                    # BROADCAST using display_name
                    broadcast_message(display_name, username, dec_msg)

                except:
                    break

        recv_thread = threading.Thread(target=receive_thread, daemon=True)
        recv_thread.start()

        # Server send loop - now broadcasts to ALL
        while username in active_clients:
            reply = input()
            if reply.lower() == "exit":
                break
            # Broadcast server message to ALL clients
            broadcast_message("MAIN", "SERVER", reply)

    except Exception as e:
        print(f"Error with {username} ({display_name}): {e}")
    finally:
        # Cleanup
        with client_lock:
            if username in active_clients:
                del active_clients[username]
        if conn:
            conn.close()
        print(
            f"Client {display_name} ({username}) disconnected. Active: {len(active_clients)}")


def broadcast_message(sender_display, sender_name, message):
    """Send message to ALL other clients using display_name (u1,u2,u3)"""
    with client_lock:
        for client_username, client_data in active_clients.items():
            try:
                # Show sender as "u1" format
                sender_info = f"{sender_display} ({sender_name})"
                enc_msg = encrypt(
                    f"[{sender_info}]: {message}", client_data['public_key'])
                client_data['conn'].send(pickle.dumps(enc_msg))
            except:
                print(f"Failed to send to {client_username}")


def server_program():
    global next_user_index
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 12345))
    s.listen(MAX_CLIENTS)
    print(
        f"Server listening on port 12345 (MAX {MAX_CLIENTS} unique clients)")
    print("Users will be assigned: u1, u2, u3 by connection order")

    while len(active_clients) < MAX_CLIENTS:
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
