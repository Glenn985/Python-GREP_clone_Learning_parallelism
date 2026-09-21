import socket
import threading

clients = {}   # client_id -> conn
clients_lock = threading.Lock() #Only one thread at a time can enter code 
#protected by that SAME clients_lock
# 
def handle_client(conn,client_id): # to get and recieve the messafges of the client, its a wholw thread of its own 
    print(f"client {client_id} connected") 
    # so for this we need to handle one client only, witht eh id that is stored int eh global thing
    #this will be used for the thread to be executed, and this is post connection
    while True:
        data = conn.recv(1024)
        if not data:
            break
        message = data.decode("utf-8")
        print(f"client {client_id}: {message}")
    ## this is to break the connection, and remove client we need to use a thread lock also if both of them say bye 
    with clients_lock:
        clients.pop(client_id,None) 
    conn.close()
    print(f"client {client_id} disconnected")




#just understand the key here is that , we want to be able ot have a pthway for server to always send message to the Client
def server_input_loop(): 
    while True:
     try: 
        client_id = int(input("Which client to send to? 0 for broadcast")) 
        if client_id ==0:
            message = input("Message: ")
            event_broadcast(message)
            continue
        with clients_lock:
           conn = clients.get(client_id) 
        if conn is not None:
            message = input("Message:")
        else:
            print("That client does not exist")
            continue
        conn.sendall(message.encode())
     except ValueError:
            print("Enter a valid client number")



def event_broadcast(message):
    with clients_lock:
        for conn in clients.values():
            conn.sendall(message.encode())


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
        if  server_sender == False:
            sender_thread = threading.Thread(
                    target=server_input_loop,
                    daemon=True)            
            sender_thread.start()
            server_sender = True
        client_id += 1
        with clients_lock:
            clients[client_id] = conn
        thread = threading.Thread(  # each client a sepearate thread
            target=handle_client,
            args=(conn, client_id)
        )
        thread.start()


if __name__ == "__main__":
    server_program()