import socket
import threading
import time
import json
my_state = {"normal": True, "Current_room": None, "Room_IDs": []}  # default state
#sednign as a custom JSON ie metadata so server can undersatnd and parse nd do it  

def message_metadata(message, my_state):
    print("Current my_state:", my_state)
    print("server state in message_metadata")
    parts = message.split()
    if not parts:
        return None 
    if parts[0].startswith("@create"):
        client_ids = []
        for p in parts[1:]:
            if p.startswith("@"):
                try:
                    client_ids.append(int(p[1:]))
                except ValueError:
                    pass
        return {
            "type": "create_room",
            "client_ids": client_ids
        }
    if parts[0].startswith("@"):
        client_ids = []
        text = ""
        for p in parts:
            try:
                if p.startswith("@"):
                    try:
                        client_ids.append(int(p[1:]))
                    except ValueError:
                        pass
                else:
                    text += p + " "
            except Exception as e:
                print("Error parsing part:", p, e)
        return {
            "type": "direct_message",
            "client_ids": client_ids,
            "message": text.strip()
        }
    if my_state["Current_room"] is not None:
        return {
            "type": "room_message",
            "room_id": my_state["Current_room"],
            "message": message
        }
    print("Current_room is None, sending as server_message")
    return {
        "type": "server_message",
        "message": message
    }
def receive_messages(client_socket, mode):
    global my_state
    buffer = ""
    while True:
        try:
            data = client_socket.recv(1024)
            #print("RAW RECEIVED:", repr(data))
            print("DECODED:", data.decode("utf-8"))

            data = json.loads(data.decode("utf-8"))  # Decode JSON data
            if not data:
                break
            if data["type"] == "state":
                my_state = data["client_mode"] 
                print(my_state)
                continue
            if data["type"] == "room_status":
                room_id = data["room_id"]
                status = data["status"]
                print(f"\nRoom {room_id} status: {status} - {data['message']}")
                continue 

            
            if data["type"] == "direct_message": 
                client_id = data["from"]
                print(f"\nDirect message from Client {client_id}: {data['message']}")
                continue

            if data["type"] == "room_message":
                room_id = data["room_id"]
                print(f"\nRoom {room_id}: ", data["message"])
            elif data["type"] == "server_message":
                print("\nServer:", data["message"])
                print(" -> ", end="", flush=True)

        except Exception as e:
            print("Receive error:", e)
            break



def recieve_messages(client_socket ):
    pass

def client_program():
    host = "127.0.0.1"
    port = 7800
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # separate thread whose ONLY job is receiving
    receiver_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket, None)
    )
    receiver_thread.start()
    # main thread can now send whenever you type
    while True:
        try:
            message = input(" -> ")
        except EOFError: 
            print("Exiting Room...")
            metadata = {
                "type": "exit_room"
            }
            json_message = json.dumps(metadata)
            client_socket.sendall(json_message.encode())
            continue

        
        metadata = message_metadata(message, my_state)
        json_message = json.dumps(metadata) if metadata else message 
        print(my_state)
        print("Sending message in client.py :", json_message)
        client_socket.sendall(json_message.encode())
     
        if message.lower().strip() == "bye":
            break
    client_socket.close()

if __name__ == "__main__":
    client_program()