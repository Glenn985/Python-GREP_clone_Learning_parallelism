import socket
import threading
import time

client = {}
client_id = 0  # SHARED VARIABLE (NO LOCK!)

client_lock = threading.Lock()

def assign_id(conn):
    global client_id
    with client_lock:
        # --- RACE CONDITION WINDOW ---
        current_id = client_id       # 1. Both threads read current_id as 0
        print(f"[{threading.current_thread().name}] Read client_id as: {current_id}")
        time.sleep(1)                 # 2. Force both threads to pause here at the same time!

        new_id = current_id + 1       # 3. Both compute 0 + 1 = 1
        client_id = new_id
        client[new_id] = conn         # 4. Both write to client[1]!
        print(f"[{threading.current_thread().name}] Overwrote client[{new_id}]")


    new_id = current_id + 1       # 3. Both compute 0 + 1 = 1
    client_id = new_id
    client[new_id] = conn         # 4. Both write to client[1]!
    print(f"[{threading.current_thread().name}] Overwrote client[{new_id}]")

def handle_client(conn, addr):
    assign_id(conn)

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 7800))
    server.listen()
    print("Server running on port 7800...")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()

if __name__ == "__main__":
    run_server()