<h1>Secure Chat Application</h1>

<h2>Description</h2>
This script is a Python-based self-hosted secure chatroom application which uses client-server model to create a end-to-end encrypted chatroom. It provides a secure communication channel for multiple users, featuring invitation-based access, security questions, and real-time encrypted messaging.
<br />

<h2>Creating a chat room:</h2>

<p align="center">
Chat room interface: <br/>
<br />
  <img src="https://i.imgur.com/RmnZwNJ.png" height="80%" width="80%" alt="Chatroom interface"/>
<br />

<h2>Features</h2>

- Client-server architecture
- End-to-end encryption using RSA
- Secure room access with invitation tokens and security questions
- Color-coded user messages
- Public and private IP support for server hosting
- Nickname support for users

<h2>Technical Details</h2>

<h3>Dependencies</h3>

- Python 3.7+
- Required libraries: socket, threading, os, base64, requests, random, pyotp, cryptography

<h3>Four layer Security Measures</h3>

1. <b>Fernet Encrypted Token(layer 1):</b> Employs Fernet for generating and encrypting invitation tokens.
2. <b>RSA Encryption(layer 2):</b> Uses 2048-bit RSA keys for secure key exchange and message encryption.
3. <b>Temporary access code(layer 3):</b> Uses One-Time code to access the chatroom
4. <b>Security Question (layer 4):</b> Adds an extra layer of authentication for joining chat rooms.

<h3>Key Components</h3>

1. <b>ChatServer Class:</b>
   - Manages client connections
   - Handles message broadcasting
   - Implements security measures

2. <b>ChatClient Class:</b>
   - Connects to the server
   - Sends and receives encrypted messages
   - Manages user interface for chatting

<h2>Usage</h2>

<h3>Running the Server</h3>

1. Run the script and choose 's' for server mode.
2. Select whether to use a private or public IP.
3. Set a security question and answer.
4. The server will display the invitation token for clients to use.
<br />
  <img src="https://i.imgur.com/Dn5QerX.png" height="80%" width="80%" alt="server side"/>
<br />

<h3>Running a Client</h3>

1. Run the script and choose 'c' for client mode.
2. Enter the invitation token provided by the server.
3. Answer the security question.
4. Enter the room code displayed on the server.
5. Choose a nickname.
6. Now we are inside the chat room
<br />
  <img src="https://i.imgur.com/YC4zmjF.png" height="80%" width="80%" alt="client side"/>
<br />
<br />
  <img src="https://i.imgur.com/2rdi8xD.png" height="80%" width="80%" alt="chatting interface"/>
<br />

<h2>Security Considerations</h2>

- The application uses strong encryption methods, but as with any security system, it should be regularly updated and audited.
- Users should be cautious about sharing invitation tokens and answers to security questions.
- While the chat is end-to-end encrypted, metadata about connections could potentially be observed by network administrators.

<h2>Future Improvements</h2>

- Implement perfect forward secrecy by using ephemeral keys.
- Add support for file transfers.
- Develop a graphical user interface.
- Implement server-side logging for better monitoring and debugging.

<h2>Disclaimer</h2>

This application is a demonstration of secure communication principles and should not be used in production environments without thorough security auditing and hardening.

<h2>License</h2>

[MIT License](https://opensource.org/licenses/MIT)

<h2>Contributing</h2>

Contributions to improve the application are welcomed. Please fork the repository and submit a pull request with your changes.
