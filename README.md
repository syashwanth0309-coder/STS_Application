# Secure Socket Communication with RSA and Hashing

## Overview
This project demonstrates a secure client–server communication system implemented in Python using **RSA encryption** and **SHA-256 hashing**. It was developed as an exercise in socket programming and cryptography, combining authentication, key exchange, and encrypted message transfer.

## Motivation
I first explored the RSA algorithm in a smaller project during my undergraduate studies. Driven by curiosity, I extended this knowledge by experimenting with Python sockets. This project gave me the opportunity to:
- Revisit and strengthen my understanding of RSA encryption.
- Gain hands-on experience with hashing for password verification.
- Explore socket-based data sharing between two devices on a shared network.

## Features
- **User Authentication**: Passwords are verified using SHA-256 hashing.
- **RSA Key Exchange**: Public keys are serialized and exchanged between client and server.
- **Encrypted Communication**: Messages are encrypted with RSA before transmission and decrypted upon receipt.
- **Bidirectional Chat**: Both server and client can send and receive secure messages.
- **Exit Handling**: Either side can terminate the session gracefully by typing `exit`.

## Project Structure
Application_textSharing/ 
├── server.py # Server-side program 
├── client.py # Client-side program 
├── utility_RSA.py # RSA key generation, encryption, decryption, serialization 
├── utility_auth.py # User authentication with SHA-256 hashing 
├── requirements.txt # Dependencies 
└── README.md # Project documentation

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/syashwanth0309-coder/Text-Sharing-Application-client-server-
   cd Application_textSharing
2. Install dependancies:
    python -m pip install -r requirements.txt
3. Run the server:
    python server.py
4. Run the client(on the same or another device in the network):
    python client.py
5. Enter Credentials when promoted. calid users are defined in utility_auth.py.

## Learning Outcomes

Through this project, I reinforced:
Practical application of RSA encryption in socket communication.
Secure password handling using SHA-256 hashing.
Network programming concepts such as TCP sockets and data serialization.

## Future Improvements

Extend to multiple clients.
Add TLS/SSL for layered security.
Implement a GUI for easier interaction.

