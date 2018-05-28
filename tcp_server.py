import socket
import threading

b_ip = "0.0.0.0"
b_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((b_ip, b_port))
# Max num of connections = 5
server.listen(5)
print "Listenting on", b_ip, b_port


def handle_client(client_socket):
    request = client_socket.recv(1024)
    print "Recieved ", request
    client_socket.send("ACK!")
    client_socket.close()
    
while True:
    client, addr = server.accept()
    print "Accepted ", addr
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
    
    
    
    




