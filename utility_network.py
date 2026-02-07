import pickle
import threading
from utility_RSA import encrypt


def broadcast_message(clients_dict, client_lock, sender_display, sender_name, message):
    """
    Unified broadcast function - works for BOTH server and client
    """
    with client_lock:
        for client_username, client_data in clients_dict.items():
            try:
                # Skip sender themselves (avoid echo)
                if client_username == sender_name and sender_display != "MAIN":
                    continue

                # Format: [Peer1 (username)]: message
                sender_info = f"{sender_display} ({sender_name})"
                formatted_msg = f"[{sender_info}]: {message}"

                # Encrypt with recipient's public key
                enc_msg = encrypt(formatted_msg, client_data['public_key'])
                client_data['conn'].sendall(pickle.dumps(enc_msg))

            except Exception as e:
                print(f"Failed to broadcast to {client_username}: {e}")
