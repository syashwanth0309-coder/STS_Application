# Secure Multi-Client Chat System (Python + RSA) 

A centralized server-client chat application built in Python that supports **encrypted communication** using RSA. The server can handle up to **3 clients simultaneously** (configurable) and broadcasts messages to all connected users in real time. 

--- 

## Features 

- Secure login with SHA-256 password hashing 
- RSA encryption for all communication 
- Full duplex messaging (send/receive simultaneously) 
- Broadcast mode: one client’s message shared with all 
- Unique peer IDs (`Peer1`, `Peer2`, `Peer3`) 
- Easily increase max clients via `MAX_CLIENTS` 

--- 

## Project Structure

├── client.py           # Client program 
├── server.py           # Server program 
├── utility_auth.py # Authentication (SHA-256) 
├── utility_RSA.py # RSA key generation & encryption

---

## Requirements
- Python 3.8+
- Libraries: `cryptography`, `pickle`, `socket`, `threading`, `hashlib`

**Install cryptography:**
    ```bash
    pip install cryptography

---

## How to Run

1. Start Server
    python server.py
    Default port: 12345
    Max clients: 3 (edit MAX_CLIENTS to change)

2. Start Client
    python client.py
    Enter username & password

    Valid users in utility_auth.py:
    users = {
    "kili": sha256("yash@143"),
    "admin": sha256("admin@1234"),
    "buddy": sha256("buddy@1234")
    }

---

## Usage

Type message → press Enter
Messages encrypted & broadcast to all peers
Type exit → disconnec

---

## Security

Passwords stored as SHA-256 hashes
RSA 2048-bit encryption
Duplicate login prevention
Unique peer IDs for clarity

---

## Example Flow

Start server
Client connects → login
Server verifies → assigns ID
RSA keys exchanged
Client sends → server broadcasts
exit → disconnect

---

## Scaling

Increase MAX_CLIENTS in server.py
Run more client.py instances


## Author
Built by S. Yashwanth — secure socket programming, RSA encryption, collaborative communication.
