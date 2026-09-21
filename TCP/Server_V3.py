import socket 
import threading
import time
from tokenize import String
import re
import json

#mode can be "normal" or "room"

def create_client_state():
    return {
        "mode": "normal",
        "Current_room": None,
        "Room_IDs": [],
        "username": None,
        "connected": True
    }
class ServerState:
    def __init__(self):
        self.clients = {}
        self.meeting_rooms = {}
        self.client_mode = {}
        self.next_room_id = 0
        self.lock = threading.Lock()


def send_json(conn, payload): 
    print(payload)
    print("At send Json for room logic")
    message = json.dumps(payload) + "\n"
    conn.sendall(message.encode("utf-8"))


def create_client_mode():
    return {
        "mode": "normal",
        "Current_room": None,
        "Room_IDs": []
    }

def enter_room(server_state, client_id, room_id):
    with server_state.lock:
        server_state.client_mode[client_id]["mode"] = "room"
        server_state.client_mode[client_id]["Current_room"] = room_id
    send_state(server_state, [client_id])


def send_state(server_state, client_ids): 
    print("We are in send_state with client_ids:", client_ids)
    i = len(client_ids) - 1
    while i >= 0:
        cid = client_ids[i]
        state = {
            "type": "state",
            "client_mode": server_state.client_mode[cid],
        }
        conn = server_state.clients[cid]
        send_json(conn, state)
        i -= 1

def broadcast(server_state, message):
    with server_state.lock:
        for conn in server_state.clients.values(): 
            send_state(server_state, server_state.clients.keys()) #this is for future wehre state is likelyto be changed
            send_json(conn, {"type": "server_message", "message": message}) 


#for sending message to client we need ot implement json , type WHICH client_id and message only
def send_message_to_client(server_state, our_id, client_ids, message): 
    metadata = {} 
    print("We are in sned message to client")
    #send_state(server_state, [our_id])  # Send updated state to the sender 
    room_id = None
    if server_state.client_mode[our_id]["mode"] == "room": ## this handles room stuff without a sedn to room comnads
        room_id = server_state.client_mode[our_id]["Current_room"] 
        send_to_room(server_state, room_id, our_id, message)
        return True

    with server_state.lock:
        for target_id in client_ids:
            conn = server_state.clients.get(target_id)
            # Client doesn't exist
            if conn is None:
                return False
            send_json(conn, {
    "type": "direct_message",
    "from": our_id,
    "message": message
})
    return True


def Create_meeting_room(server_state, room_id, client_ids):
    with server_state.lock:
        server_state.meeting_rooms[room_id] = []
        for cid in client_ids:
            if cid in server_state.clients:
                server_state.meeting_rooms[room_id].append(cid) 
                server_state.client_mode[cid]["mode"] = "room"
                server_state.client_mode[cid]["Current_room"] = room_id 
                server_state.client_mode[cid]["Room_IDs"].append(room_id)
    send_state(server_state, client_ids)  # Send updated state to all clients added to the room

def send_to_room(server_state, room_id, sender_id, message):
    print("We are in the send to room")
    if sender_id not in server_state.meeting_rooms.get(room_id, []):
        print(f"Sender {sender_id} is not in room {room_id}") 
        client_conn = server_state.clients.get(sender_id)
        client_conn.sendall(f"You are not in room {room_id}".encode("utf-8"))
        return False
    with server_state.lock:
        if room_id not in server_state.meeting_rooms:
            return False
        for cid in server_state.meeting_rooms[room_id]:
            print("ROOM MEMBERS:", server_state.meeting_rooms)
            print("CURRENT ROOM MEMBERS:", server_state.meeting_rooms.get(room_id))
            print("SENDER:", sender_id)
            if cid == sender_id:
                continue  

            print(f"Sending message to client {cid} in room {room_id}")
            print(cid)
            conn = server_state.clients.get(cid)
            if conn:  
                print(f"Sending message to client {cid} in room {room_id}")
                metadata = {
                "type": "room_message",
                "room_id": room_id,
                "from": sender_id,
                "message": message
                }
                send_json(conn, metadata)
    return True

def handle_client(server_state, client_id):
    # Get this client's socket once
    with server_state.lock:
        conn = server_state.clients[client_id]
    print(f"Thread start for client {client_id}")
    while True:
        try:
            # RECEIVE DATA
            data = conn.recv(1024)
            if not data:
                print(f"Client {client_id} disconnected")
                break
            message = data.decode("utf-8")
            #print("RAW DATA:", repr(data))
            #print("MESSAGE:", repr(message))
            # Convert JSON string -> Python dictionary
            request = json.loads(message)
            request_type = request.get("type")
            print("REQUEST:", request)
            print("State also " ,server_state.client_mode[client_id])
     
            # EXIT ROOMW
            if request_type == "exit_room":
                with server_state.lock:
                    server_state.client_mode[client_id]["mode"] = "normal"
                    server_state.client_mode[client_id]["Current_room"] = None
                send_state(server_state, [client_id])
                continue
            if request_type == "server_message": 
                print("We are here in the server Message")
                message_text = request["message"]
                # Check whether client is currently inside a room
                with server_state.lock:
                    mode = server_state.client_mode[client_id]["mode"]
                    current_room = server_state.client_mode[client_id].get(
                        "Current_room"
                    )
                # If they're in a room, send the message to that room
                if mode == "room" and current_room is not None:
                    send_to_room(
                        server_state,
                        current_room,
                        client_id,
                        message_text
                    )
                else:
                    print(
                        f"Server message from client "
                        f"{client_id}: {message_text}"
                    )
                continue

            if request_type == "room_message":
                print("In server_v3.py in the room message section")
                print("Request received for room message:", request)
                room_id = request["room_id"]
                message_text = request["message"] 
                print("WE are calling the function send to room,", room_id, client_id, message_text)
                send_to_room(
                    server_state,
                    room_id,
                    client_id,
                    message_text
                )
                continue 


            if request_type == "direct_message":
                print("In server_v3.py in the direct message section") 
                print("Request received for direct message:", request)
                client_target_ids = request["client_ids"]
                print("Target client IDs for direct message:", client_target_ids)
                message_text = request["message"]
                print("Message text for direct message:", message_text)
                try:
                    success = send_message_to_client(
                        server_state,
                        client_id,
                        client_target_ids,
                        message_text.strip()
                    )
                    if not success:
                        conn.sendall(
                            f"Client {client_target_ids} does not exist".encode(
                                "utf-8"
                            )
                        )
                except ValueError:
                    print(
                        "Invalid message format. "
                        "Use @<client_id> <message>"
                    )
                continue
            if request_type == "create_room":
                client_target_ids = request["client_ids"]
                print(
                    f"Client {client_id} wants room with:",
                    client_target_ids ## the client target IDs contain the IDs of the clients to be added to the room
                )
                with server_state.lock:
                    server_state.next_room_id += 1
                    new_room_id = server_state.next_room_id ## logic is just to increment previous to get the current Room ID
                    print("Room creating with ID:", new_room_id)
                    # Store room ID for creator 
                    server_state.client_mode[client_id]["Room_IDs"] = [new_room_id] 
                # Make sure creator is also included
                room_members = [client_id]
                for cid in client_target_ids:
                    if cid not in room_members: ## this is to avoid the duplicate of hte creator 
                        room_members.append(cid)
                # Actually create room
                Create_meeting_room(
                    server_state,
                    new_room_id,
                    room_members
                )
                # Put main person in the room 
                with server_state.lock:
                    server_state.client_mode[client_id]["mode"] = "room"
                    server_state.client_mode[client_id]["Current_room"] = (new_room_id)
                send_state(
                    server_state,
                    [client_id])  

                
                room_status = {
                "type": "room_status",
                "status": "joined",
                "room_id": new_room_id,
                "message": f"You are in Room {new_room_id}"
                }
                send_json(conn, room_status)

                continue
            print(
                f"Unknown request type from client {client_id}:",
                request_type
            )
        except json.JSONDecodeError as e:
            print(
                f"Invalid JSON from client {client_id}:",
                repr(message)
            )
            print("JSON error:", e)
        except ConnectionResetError:
            print(
                f"Connection reset by client {client_id}"
            )
            break
        except KeyError as e:
            print(
                f"Missing field from client {client_id}:",
                e
            )
        except Exception as e:
            print(
                f"Unexpected error for client {client_id}:",e)
            break
    with server_state.lock:
        server_state.clients.pop(client_id, None)
        server_state.client_mode.pop(client_id, None)
    conn.close()
    print(f"Client {client_id} cleaned up")

# here we just want to be able to communicate to the client we need to
def server_communication(server_state):
    while True:
        client_id = int(input("Which client to send to ? \n"))

        if client_id == 0:
            message = input("Message:")
            broadcast(server_state, message)
            continue
        with server_state.lock:
            conn = server_state.clients.get(client_id)
        if conn is None:
            print(f"Client {client_id} does not exist")
            continue
        message = input("Enter message: ")
        message = "Server: " + message
        conn.sendall(message.encode("utf-8"))


def server_program():
    host = "127.0.0.1"
    port = 7800
    server_state = ServerState()
    server_sender = False
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )
    server_socket.bind((host, port))
    server_socket.listen()
    print("Server listening on", port)
    client_id = 0




    while True:
        conn, address = server_socket.accept()
        print(f"Connection from {address} \n")
        if server_sender == False:
            sender_thread = threading.Thread(
                target=server_communication,
                args=(server_state,),
                daemon=True
            )
            sender_thread.start()
            server_sender = True
        client_id += 1

        with server_state.lock:
         server_state.clients[client_id] = conn
         server_state.client_mode[client_id] = create_client_mode()


        with server_state.lock:
            server_state.clients[client_id] = conn
            server_state.client_mode[client_id] = {
                "mode": "normal",
                "Current_room": None,
                "Room_IDs": []
            }
        print("AGAIN HERE BTW")
        thread = threading.Thread(
            target=handle_client,
            args=(server_state, client_id)
        )

        print("Thread start")
        thread.start()


if __name__ == "__main__":
    server_program()