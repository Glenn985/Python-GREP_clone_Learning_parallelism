import socket 
import threading
import time
from tokenize import String
import re
import json


client = {} # this can handle state also  default mode will be normal
Meeting_room = {}
current_room = 0
room_id = 0 
client_mode = {


} # to handlemode, all the rooms present in , current_room present
#meeting room will be 1


import json
def send_state(client_id):
    state = client_mode[client_id]
    payload = "STATUS|" + json.dumps(state)

    conn = client[client_id]
    conn.sendall(payload.encode("utf-8"))




client_lock = threading.Lock() # we cant create new locks same lock 
def broadcast(message):
    with client_lock:
        for conn in client.values():
            conn.sendall(message.encode("utf-8"))


def send_message_to_client(our_id, client_ids, message): 
    if client_mode[our_id]["mode"] == "room":
        room_id = client_mode[our_id]["Current_room"]
        if room_id is None:  # Get the last room ID
            room_id = client_mode[our_id]["Room_IDs"][-1]
        return send_to_room(room_id, our_id, message)
        return True

    with client_lock:
        for target_id in client_ids:
            conn = client.get(target_id)
            # Client doesn't exist
            if conn is None:
                return False

            Message = f"{our_id}: {message}"
            conn.sendall(Message.encode("utf-8"))
        
    return True



def Create_meeting_room(room_id, client_ids):
    client_id_list = re.findall(r"\d+", client_ids)
    client_id_list = [int(cid) for cid in client_id_list]

    with client_lock:
        Meeting_room[room_id] = []
        for cid in client_id_list:
            if cid in client:
                Meeting_room[room_id].append(cid)



def send_to_room(room_id, sender_id, message):
    print("We are in the send to room")

    if sender_id not in Meeting_room.get(room_id, []):
        print(f"Sender {sender_id} is not in room {room_id}") 
        client_conn = client.get(sender_id)
        client_conn.sendall(f"You are not in room {room_id}".encode("utf-8"))
        return False
    
    with client_lock:
        if room_id not in Meeting_room:
            return False
        for cid in Meeting_room[room_id]:
            if cid == sender_id:
                continue
            conn = client.get(cid)
            if conn:
                conn.sendall(
                    f"Room {room_id} - {sender_id}: {message}".encode("utf-8")
                )
    return True



def handle_client(client_id):
    global room_id
    with client_lock:
        conn = client[client_id]
    while True:
        try:
            data = conn.recv(1024)
            message = data.decode("utf-8")
            if data == b"":
                client.pop(client_id,None) # we dont want the clietn . THIS IS basicly showing when after a thread is done, the clietn
                break
            parts = message.split() # splits by space 
            client_target_id = []
            Buffer = "" 
            for part in parts:
                if part.startswith("@"):
                    try:
                        target_id = int(part[1:])  # removes @
                        client_target_id.append(target_id)
                        continue #now we remove the @
                    except ValueError:
                        pass 
                Buffer = Buffer + part + " "

            if message.startswith("#create"):
                print("True") 
                room_id = room_id + 1
                print("Room creating with ID:", room_id) 
                if "Room_IDs" not in client_mode[client_id]:
                    client_mode[client_id]["Room_IDs"] = [room_id]
                else:
                    client_mode[client_id]["Room_IDs"].append(room_id)


                Create_meeting_room(room_id,message) 
                client_mode[client_id]["mode"] = "room"
                send_state(client_id)

                conn = client[client_id] 
                message = "You are in Room"
                conn.sendall(message.encode("utf-8")) 
                print(client_mode[client_id]["mode"]) 

                client_mode[client_id]["Current_room"] = room_id 
            else:
                print("False")


            if message[0] == "@":
                try:
                    if not send_message_to_client(client_id,client_target_id, Buffer.strip()):
                        conn.sendall(f"Client {client_target_id} does not exist".encode("utf-8"))
                except ValueError:
                    print("Invalid message format. Use @<client_id> <message>")
                continue  
            print(f"client {client_id}: {message}")
        except ConnectionResetError:
            print(f"connection error with client {client_id}")
            break 


        if message.startswith("#") or client_mode[client_id]["mode"] == "room":  
                room_id_get = client_mode[client_id]["Current_room"] 
                room_id_match = re.search(r'\d+', message)
                if room_id_match:
                    room_id = int(room_id_match.group())
                    send_to_room(room_id, client_id, message)
                    continue 

                if room_id_get:
                    send_to_room(room_id_get, client_id, message)
                    continue
    


    with client_lock:
        client.pop(client_id,None) # removes the client id because we dont want it 


# here we just want to be bale to communicate to the client we need to 
def server_communication():
    while True:
        client_id = int(input("Which client to send to ? \n")) 
        if client_id ==0:
            message = input("Message:") 
            broadcast(message) 
            continue 

        conn = client.get(client_id)
        if conn is None:
            print(f"Client {client_id} does not exist")
            continue # this pushes back to the while loop  

        message = input("Enter message: ")
        message = "Server: " + message
        conn.sendall(message.encode("utf-8"))
     


def server_program():
    host = "127.0.0.1"
    port = 7800
    server_sender = False
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )
    server_socket.bind((host, port))
    server_socket.listen()
    print("Server listening on", port) 
    # separate thread for SERVER keyboard input
    client_id = 0
    while True: 
        conn, address = server_socket.accept() 
        print(f"Connection from {address} \n") # this is so that we sinply dont output the message 
        if  server_sender == False:
            sender_thread = threading.Thread(
                    target=server_communication,
                    daemon=True)            
            sender_thread.start()
            server_sender = True
        client_id += 1
        with client_lock:
            client[client_id] = conn 
            client_mode[client_id] = {"mode": "normal"}  # default mode is normal 


        print("AGAIN HERE BTW")
        thread = threading.Thread(  # each client a sepearate thread
            target=handle_client,
            args=(client_id,)
        )
        print("Thread start")
        thread.start()


if __name__ == "__main__":
    server_program()


# ran into a problem wehre i cldnt treat the noraml b as a disconnect, i dint 