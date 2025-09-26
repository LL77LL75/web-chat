import socket
import threading
import random
import os
import json

# Encoding and Decoding Functions
c2n = {**{chr(i + 96): i for i in range(1, 27)}, " ": 27, ",": 28, ".": 29, "!": 30, "/": 31}
n2c = {v: k for k, v in c2n.items()}

def enc(t):
    result = []
    for ch in t.lower():
        b = bin(c2n[ch])[2:]
        i = 0
        while i < len(b):
            g = random.choice([2, 3])
            segment = b[i:i + g].ljust(g, "0")
            result.append(int(segment, 2))
            i += g
    return result

def dec(d):
    return "".join(
        n2c[int("".join(bin(g)[2:].zfill(2 if g < 4 else 3) for g in grp).lstrip("0") or "0", 2)]
        for grp in d
    )

# File Paths
USERNAMES_FILE = "usernames.txt"
PASSWORDS_FILE = "passwords.txt"
RANKS_FILE = "ranks.txt"
ROOMS_FILE = "rooms.json"

# Load Users, Passwords, Ranks
def load_users():
    with open(USERNAMES_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def load_passwords():
    with open(PASSWORDS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def load_ranks():
    with open(RANKS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_rooms(rooms):
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f)

def load_rooms():
    if os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, "r") as f:
            return json.load(f)
    return {}

# User Authentication
def authenticate_user():
    users = load_users()
    passwords = load_passwords()
    ranks = load_ranks()

    print("Enter your username:")
    username = input().strip()

    if username not in users:
        print("Username not found.")
        return None, None

    index = users.index(username)
    print("Enter your password:")
    password = input().strip()

    if password != passwords[index]:
        print("Incorrect password.")
        return None, None

    rank = ranks[index]
    print(f"Welcome {username} ({rank} admin)")

    change_credentials(username)  # Allow the user to change credentials

    return username, rank

# Change Credentials
def change_credentials(username):
    print("Do you want to change your username and/or password? (yes/no)")
    response = input().strip().lower()
    if response == 'yes':
        print("Enter new username:")
        new_username = input().strip()
        print("Enter new password:")
        new_password = input().strip()
        if update_credentials(username, new_username, new_password):
            username = new_username  # Update the username in the session

# Update Credentials
def update_credentials(old_username, new_username, new_password):
    users = load_users()
    passwords = load_passwords()
    ranks = load_ranks()

    if old_username not in users:
        print("Username not found.")
        return False

    index = users.index(old_username)
    users[index] = new_username
    passwords[index] = new_password

    with open(USERNAMES_FILE, "w") as f:
        f.writelines([f"{user}\n" for user in users])
    with open(PASSWORDS_FILE, "w") as f:
        f.writelines([f"{password}\n" for password in passwords])

    print("Credentials updated successfully.")
    return True

# Room Management
def create_room(code):
    rooms = load_rooms()
    if code in rooms:
        print(f"Room {code} already exists.")
        return None
    rooms[code] = {"hosts": [], "members": [], "bans": {"users": [], "by": []}, "mutes": {"users": [], "by": []}}
    save_rooms(rooms)
    print(f"Room {code} created.")
    return rooms[code]

def shutdown_room(code):
    rooms = load_rooms()
    if code not in rooms:
        print(f"Room {code} does not exist.")
        return
    del rooms[code]
    save_rooms(rooms)
    print(f"Room {code} has been shut down.")

def list_rooms():
    rooms = load_rooms()
    if not rooms:
        print("No active rooms.")
        return
    print("Active rooms:")
    for code, details in rooms.items():
        print(f"Code: {code}, Hosts: {len(details['hosts'])}, Members: {len(details['members'])}")

def list_banned_users(room_code):
    rooms = load_rooms()
    room = rooms.get(room_code)
    if room:
        if room["bans"]["users"]:
            print("Banned Users:")
            for user, admin in zip(room["bans"]["users"], room["bans"]["by"]):
                print(f"{user} (Banned by {admin})")
        else:
            print("No banned users.")
    else:
        print(f"Room {room_code} does not exist.")

def list_muted_users(room_code):
    rooms = load_rooms()
    room = rooms.get(room_code)
    if room:
        if room["mutes"]["users"]:
            print("Muted Users:")
            for user, admin in zip(room["mutes"]["users"], room["mutes"]["by"]):
                print(f"{user} (Muted by {admin})")
        else:
            print("No muted users.")
    else:
        print(f"Room {room_code} does not exist.")

# Admin Commands
def promote_user(username, rank):
    if rank == "core":
        print("You cannot promote yourself to core.")
        return
    users = load_users()
    ranks = load_ranks()
    if username not in users:
        print("User not found.")
        return
    index = users.index(username)
    ranks[index] = "core"
    with open(RANKS_FILE, "w") as f:
        f.writelines([f"{r}\n" for r in ranks])
    print(f"{username} has been promoted to core admin.")

# Main Server Loop
def handle_client(client_socket, addr):
    username, rank = authenticate_user()
    if not username:
        client_socket.close()
        return

    client_socket.send(enc("Welcome to the chat server!").encode())

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.lower() == "exit":
                break
            print(f"Received message from {username}: {message}")
            client_socket.send(enc(f"Echo: {message}").encode())
        except Exception as e:
            print(f"Error handling message from {username}: {e}")
            break

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)
    print("Server listening on port 5555...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    start_server()
