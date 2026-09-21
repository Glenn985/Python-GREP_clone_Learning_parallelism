import socket
import threading
import time
import json

my_state = {"normal": True, "mode": "normal", "Current_room": None, "Room_IDs": []}  # default state



def receive_messages(client_socket,mode):
    while True:
        try: 
            
            data = client_socket.recv(1024)
            # if mode == "slow":
                # time.sleep(4) # simulate a slow connection
            if not data:
                break

            message = data.decode("utf-8")
            if not message.startswith("Server:"):

                print("\nClient", message)
                continue

            
            if message.startswith("STATUS"):
                state_json = message.split("|", 1)[1]
                my_state = json.loads(state_json) 

                continue


            if my_state["mode"] == "room":
                room_id = my_state["Current_room"]
                print(f"\nRoom {room_id}: ", message)
            else:
             print("\nServer:", message)
             print(" -> ", end="", flush=True)# immediately flushes the otuputb uffer isntead of hodling in the memory

        except:
            break


def client_program():
    host = "127.0.0.1"
    port = 7800
    mode = input("Enter mode (fast/slow): ").strip().lower()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # separate thread whose ONLY job is receiving
    receiver_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,mode,)
    )
    receiver_thread.start()
    # main thread can now send whenever you type
    while True:
        message = input(" -> ")

        if mode == "slow":
            time.sleep(5)


        client_socket.sendall(message.encode())


        if message.lower().strip() == "bye":
            break
    client_socket.close()


if __name__ == "__main__":
    client_program()