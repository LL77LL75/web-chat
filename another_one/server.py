import asyncio
import websockets
import json

USERS = {}  # websocket -> username
ROOMS = {}  # room_code -> { "hosts": [], "members": [] }

async def register(ws, username):
    USERS[ws] = username
    await ws.send(json.dumps({"type": "system", "msg": f"Welcome {username}!"}))

async def unregister(ws):
    username = USERS.get(ws)
    if username:
        del USERS[ws]
        # Remove user from all rooms
        for room in ROOMS.values():
            if username in room["members"]:
                room["members"].remove(username)

async def handle_message(ws, message):
    data = json.loads(message)

    # Join Room
    if data["type"] == "join":
        room_code = data["room"]
        username = USERS[ws]
        if room_code not in ROOMS:
            ROOMS[room_code] = {"hosts": [username], "members": []}
        ROOMS[room_code]["members"].append(username)
        await ws.send(json.dumps({"type": "system", "msg": f"Joined room {room_code}"}))

    # Chat Message
    elif data["type"] == "chat":
        room_code = data["room"]
        username = USERS[ws]
        msg = data["msg"]
        if room_code in ROOMS:
            for client, user in USERS.items():
                if user in ROOMS[room_code]["members"] or user in ROOMS[room_code]["hosts"]:
                    await client.send(json.dumps({"type": "chat", "user": username, "msg": msg}))

async def handler(ws):
    try:
        async for message in ws:
            data = json.loads(message)
            if data["type"] == "register":
                await register(ws, data["username"])
            else:
                await handle_message(ws, message)
    finally:
        await unregister(ws)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
