import socket
t_host = "127.0.0.1"
t_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client2.bind((t_host,t_port))
client.sendto("AAABBBCCC", (t_host, t_port))

data,addr = client2.recvfrom(4096)



print data,addr 