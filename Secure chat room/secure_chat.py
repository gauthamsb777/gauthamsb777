import socket
import threading
import os
import base64
import requests
import random
import pyotp
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

# ANSI color codes
RESET = '\033[0m'  # Reset to default color

WELCOME_ART = """
Welcome to the Secure Chat Room!
"""

class ChatServer:
    def __init__(self):
        self.private_ip = self.get_private_ip()
        self.public_ip = self.get_public_ip()
        self.host = None
        self.port = 8888  # Set the port directly to 8888
        self.security_question = None
        self.security_answer = None
        self.clients = {}
        self.nicknames = {}
        self.user_colors = {}
        self.lock = threading.Lock()
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.fernet_key = base64.urlsafe_b64encode(os.urandom(32))  # Generate a valid Fernet key

    def get_private_ip(self):
        return socket.gethostbyname(socket.gethostname())

    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org').text
        except:
            return "Unable to get public IP"

    def select_ip(self):
        while True:
            choice = input("Do you want to use private IP or public IP? (private/public): ").lower()
            if choice == 'private':
                self.host = self.private_ip
                print(f"Using private IP: {self.host}")
                break
            elif choice == 'public':
                self.host = ''  # Use an empty string to listen on all available interfaces
                print(f"Listening on all interfaces. Public IP: {self.public_ip}")
                break
            else:
                print("Invalid choice. Please enter 'private' or 'public'.")

    def generate_invitation_token(self):
        data = f"{self.public_ip}:{self.port}:{self.security_question}"
        fernet = Fernet(self.fernet_key)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(self.fernet_key + encrypted_data).decode()

    def decrypt_invitation_token(self, token):
        try:
            decoded_token = base64.urlsafe_b64decode(token.encode())
            fernet_key = decoded_token[:44]  # Fernet keys are 44 bytes when base64 encoded
            encrypted_data = decoded_token[44:]
            fernet = Fernet(fernet_key)
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            _, port, question = decrypted_data.split(':', 2)
            return int(port), question
        except Exception as e:
            print(f"Error decrypting token: {e}")
            return None, None

    def start(self):
        self.select_ip()
        self.security_question = input("Set a security question: ")
        self.security_answer = input("Set the answer to the security question: ")

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.host, self.port))
            server.listen(5)
            print(f"Server started on {self.host if self.host else 'all interfaces'}:{self.port}")
            print(f"Invitation token: {self.generate_invitation_token()}")
            
            while True:
                client_socket, addr = server.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.start()
        except Exception as e:
            print(f"An error occurred while starting the server: {e}")
            print("Please check your IP address and port, and ensure they are available.")

    def handle_client(self, client_socket, addr):
        try:
            # Receive and verify invitation token
            token = client_socket.recv(1024).decode()
            _, question = self.decrypt_invitation_token(token)
            if question != self.security_question:
                client_socket.send("Invalid token".encode())
                return

            # Send security question
            client_socket.send(self.security_question.encode())

            # Receive and verify security answer
            answer = client_socket.recv(1024).decode()
            if answer.lower() != self.security_answer.lower():
                client_socket.send("Incorrect answer".encode())
                return

            # Generate and display room code
            totp = pyotp.TOTP(pyotp.random_base32(), interval=60)  # Generate a new TOTP for each client
            room_code = totp.now()
            print(f"New client attempting to connect. Room code: {room_code}")
            
            # Prompt client to enter room code
            client_socket.send("Please enter the room code:".encode())

            # Wait for client to enter room code
            client_code = client_socket.recv(1024).decode()
            if client_code != room_code:
                client_socket.send("Invalid room code".encode())
                return

            # Key exchange and authentication
            client_public_key = self.key_exchange(client_socket)
            if not client_public_key:
                return

            client_socket.send("Authentication successful".encode())

            # Send welcome message
            client_socket.send(WELCOME_ART.encode())

            # Receive client's nickname
            nickname = client_socket.recv(1024).decode()
            with self.lock:
                self.clients[addr] = (client_socket, client_public_key)
                self.nicknames[addr] = nickname
                self.user_colors[addr] = f'\033[{random.randint(91, 96)}m'

            print(f"New client connected: {nickname} ({addr})")

            # Broadcast join message
            join_message = f"{nickname} has joined the chat!"
            self.broadcast(join_message, addr, system_message=True)

            while True:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break
                decrypted_message = self.private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()
                print(f"Received from {nickname} ({addr}): {decrypted_message}")
                self.broadcast(decrypted_message, addr)

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            self.remove_client(addr)

    def remove_client(self, addr):
        with self.lock:
            if addr in self.clients:
                client_socket, _ = self.clients[addr]
                del self.clients[addr]
                if addr in self.nicknames:
                    nickname = self.nicknames[addr]
                    del self.nicknames[addr]
                    del self.user_colors[addr]
                    leave_message = f"{nickname} has left the chat."
                    self.broadcast(leave_message, None, system_message=True)
                client_socket.close()

    def key_exchange(self, client_socket):
        # Send server's public key
        client_socket.send(self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

        # Receive client's public key
        client_public_key_pem = client_socket.recv(1024)
        client_public_key = serialization.load_pem_public_key(client_public_key_pem)

        # Authenticate client
        challenge = os.urandom(32)
        encrypted_challenge = client_public_key.encrypt(
            challenge,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        client_socket.send(encrypted_challenge)
        response = client_socket.recv(1024)
        if response != challenge:
            client_socket.send("Authentication failed".encode())
            return None

        return client_public_key

    def broadcast(self, message, sender, system_message=False):
        sender_nickname = self.nicknames.get(sender, "Server")
        sender_color = self.user_colors.get(sender, '') if sender else ''
        full_message = message if system_message else f"{sender_color}{sender_nickname}: {message}{RESET}"
        with self.lock:
            for addr, (client_socket, public_key) in self.clients.items():
                if addr != sender or system_message:
                    try:
                        encrypted_message = public_key.encrypt(
                            full_message.encode(),
                            padding.OAEP(
                                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(),
                                label=None
                            )
                        )
                        client_socket.send(encrypted_message)
                    except Exception as e:
                        print(f"Error sending message to {addr}: {e}")
                        self.remove_client(addr)
        print(f"Broadcast: {full_message}")

class ChatClient:
    def __init__(self, invitation_token):
        self.invitation_token = invitation_token
        self.socket = None
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.server_public_key = None
        self.nickname = None

    def connect(self):
        try:
            decoded_token = base64.urlsafe_b64decode(self.invitation_token.encode())
            fernet_key = decoded_token[:44]  # Fernet keys are 44 bytes when base64 encoded
            encrypted_data = decoded_token[44:]
            fernet = Fernet(fernet_key)
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            ip, port, _ = decrypted_data.split(':', 2)
        except Exception as e:
            print(f"Invalid invitation token: {e}")
            return False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((ip, int(port)))
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

        # Send invitation token
        self.socket.send(self.invitation_token.encode())

        # Receive and answer security question
        question = self.socket.recv(1024).decode()
        print(f"Security Question: {question}")
        answer = input("Your answer: ")
        self.socket.send(answer.encode())

        # Receive prompt for room code
        prompt = self.socket.recv(1024).decode()
        print(prompt)

        # Enter and send room code
        room_code = input("Enter the room code: ")
        self.socket.send(room_code.encode())

        # Key exchange and authentication
        if not self.key_exchange():
            return False

        # Receive and print welcome message
        welcome_art = self.socket.recv(1024).decode()
        print(welcome_art)

        # Send nickname
        self.nickname = input("Enter your nickname: ")
        self.socket.send(self.nickname.encode())

        print("Connected to server")
        return True

    def key_exchange(self):
        # Receive server's public key
        server_public_key_pem = self.socket.recv(1024)
        self.server_public_key = serialization.load_pem_public_key(server_public_key_pem)

        # Send client's public key
        self.socket.send(self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

        # Authenticate
        encrypted_challenge = self.socket.recv(1024)
        challenge = self.private_key.decrypt(
            encrypted_challenge,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.socket.send(challenge)

        auth_result = self.socket.recv(1024).decode()
        if auth_result != "Authentication successful":
            print(auth_result)
            return False
        return True

    def send_message(self, message):
        encrypted_message = self.server_public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.socket.send(encrypted_message)

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.socket.recv(1024)
                if not encrypted_message:
                    print("\nDisconnected from server.")
                    break
                message = self.private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()
                print(f"\n{message}")
                print("Enter your message: ", end="", flush=True)
            except ConnectionResetError:
                print("\nServer connection lost.")
                break
            except Exception as e:
                print(f"\nError receiving message: {e}")
                break
        self.socket.close()

    def start(self):
        if self.connect():
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            try:
                while True:
                    message = input("Enter your message: ")
                    if message.lower() == 'quit':
                        break
                    self.send_message(message)
            except KeyboardInterrupt:
                print("\nDisconnecting from the server...")
            finally:
                self.socket.close()

# Usage
if __name__ == "__main__":
    choice = input("Enter 's' for server, 'c' for client: ")
    if choice.lower() == 's':
        server = ChatServer()
        server.start()
    elif choice.lower() == 'c':
        invitation_token = input("Enter the invitation token: ")
        client = ChatClient(invitation_token)
        client.start()
    else:
        print("Invalid choice. Please enter 's' for server or 'c' for client.")
