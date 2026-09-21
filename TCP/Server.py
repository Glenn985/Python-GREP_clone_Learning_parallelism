import socket

def server_program():
    host = '127.0.0.1' ## using a host adress always the host address 
    port = 7800 
    #for creating a  conn we need a socket first 
    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #this creates a IPv4 TCP socket
    ##SOCK_STREAM is used for TCP connection, SOCKDGRAM is UDP, socket.AF_INET is for IPv4
    Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow port reuse immediately after server shutdown
    Socket.bind((host, port)) # we are binding the socket to the host and port
    ## all of this is the foundation of the  TCB 
    Socket.listen(3) ##upto 3 connections, later we can do async to run many connections on a single thread
    while True:
      conn,address = Socket.accept() #this is where it accepts any random connection,
      print("Connection from:" + str(address))
      while True:
        
        data = conn.recv(1024).decode('utf-8')

        if not data:
            break # this is because , data is always recieving, if we receive 
            # empty byte hten we break 
        
        
        print("from connected user: " + str(data))

        if data.lower().strip() == "bye":
            print("client died")
            break  
        data = input(' -> ')
        conn.sendall(data.encode())
    Socket.close() 

if __name__ == '__main__':
    server_program()
    