#!/usr/bin/env python

import sys
import socket
import threading


def hexdump(src, length=16):
    result = []
    digits = 4if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X"%(digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04x %-*s %s"%(i, length*(digits + 1), hexa, text))
    
def recieve_from(connection):
    buffer = ""
    # 2 sec timer
    connection.settimeout(2)
    try:
        # keep readin until timeout or no data
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    
    return buffer

def request_handler(buffer):
    #modify requests before being sent out
    return buffer

def response_handler(buffer):
    #modify packets before being sent out
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, recieve_first):
    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    
    #recieve data from the remote end if necessary
    if recieve_first:
        remote_buffer = recieve_from(remote_socket)
        hexdump(remote_buffer)
        
        #send it to our response handler
        remote_buffer = response_handler(remote_buffer)
        
        #if we have data send it to our local client
        if len(remote_buffer):
            print "[<==] Sending %d bytes to localhost"%len(remote_buffer)
            client_socket.send(remote_handler)
    
    # loop read from local,
    # send to remote, send to local,
    # rinse, wash, repeat
    while True:
        #read from local
        local_buffer = recieve_from(client_socket)
        
        if len(local_buffer):
            print "[==>] Recieved %d bytes from localhost." %len(local_buffer)
            hexdump(local_buffer)
            
            #send to request handler
            local_buffer = request_handler(local_buffer)
            
            #send data to remote host
            remote_socket.send(local_buffer)
            print "[==>] Sent to remote."
        
        remote_buffer = recieve_from(remote_socket)
        
        
        if len(remote_buffer):
            print "[<==] Recieved %d bytes from remotehost." %len(remote_buffer)
            hexdump(remote_buffer)
            
            #send to request handler
            remote_buffer = response_handler(remote_buffer)
            
            #send data to remote host
            remote_socket.send(remote_buffer)
            print "[<==] Sent to localhost."
        #if no more data, close connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print "[*] No more data, closing connections"
            break
  
def server_loop(local_host, local_port, remote_host, remote_port, recieve_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print "[!!] Failed to listen on %s:%d"%(local_host, local_port)
        print "[!!] Check for other listening sockets or correct permissions."
        print e
        sys.exit(0)
    
    print "[*] Listening on %s:%d"%(local_host, local_port)
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        #print connection info
        print "[==>]Recieved incoming connection from %s:%d"%(addr[0],addr[1])
        #start a thread to talk to remote host
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket,remote_host
                                              ,remote_port,recieve_first))
        proxy_thread.start()

def main():
    #no fancy command line parsing
    nm = sys.argv[1:]
    print nm
    if len(sys.argv[1:]) != 5:
        print "Usage: ./tcp_proxy.py [localhost] [localport]" \
              + " [remotehost] [remoteport] [recieve_first]"
        print "Example: ./tcp_proxy 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)
    #setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    #setup remote host
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    #connect and recieve data before sending to 
    #remote host
    recieve_first = sys.argv[5]
    
    if "True" in recieve_first:
        recieve_first = True
    else:
        recieve_first = False
        
    # now spin up listening socket 
    server_loop(local_host, local_port, remote_host, remote_port, recieve_first)

main()
    
    
    
    
    