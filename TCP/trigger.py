import socket
import threading
import time

def connect_client(name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 7800))
    print(f"Client {name} connected!")
    time.sleep(5) # Keep connection alive

# Launch TWO connections at the EXACT same millisecond
t1 = threading.Thread(target=connect_client, args=("Alice",))
t2 = threading.Thread(target=connect_client, args=("Bob",))

t1.start()
t2.start()