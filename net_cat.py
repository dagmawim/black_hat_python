#!/usr/bin/env python 
import sys
import threading
import socket
import getopt
import subprocess

#globals
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port  = 0


def usage():
    print "Net Tool"
    print
    print "Usage: file.py -t target_host -p port"
    print " -l --listen     - listen on [host]:[port] for oncoming connections"
    print " -e --execute=file_to_run - execute the given file upon recieving a connection"
    print " -c --command  -initialize the command line shell"
    print " -u --upload=destination -upon recieving connection upload a file and write to destination"
    print
    print
    print "Examples: "
    print " file.py -t 192.168.0.1 -p 5555 -l -c"
    print " file.py -t 192.168.0.1 -p 5555 -l -u=c:\\\\target.exe"
    print " file.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print " echo 'ABCDEF' | ./file.py -t 192.168.11.12 -p 135 "
    sys.exit(0)
    
    
    
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #connect to target
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)
        while True:
            #wait for data block
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print response
            #wait for more input
            buffer = raw_input("")
            buffer += "\n"
            #send
            client.send(buffer)
    except Exception as e:
        print "Exception caught, exiting"
        print e
        client.close()
    
    
    
def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        # spin off a thread
        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket,))
        client_thread.start()
        
def run_command(command):
    # trim the new line
    command = command.rstrip()
    
    try:
        output = subprocess.check_output(command,
                                         stderr=subprocess.STDOUT,
                                         shell=True)
    except Exception as e:
        output = "Failed to execute command" + str(e)
    
    return output

        
def client_handler(client_socket):
    global upload, execute, command
    #check for upload
    if len(upload_destination):
        # read in bytes and write out to file 
        file_buffer = ""
        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            # ack that we wrote the file out
            client_socket.send("Successfully saved file %s\r\n"
                               %upload_destination)
        except Exception as e:
            client_socket.send("Failed to save file %s \r\n"
                               %str(e))
    # check for command execution
    if len(execute):
        #run the command
        output = run_command(execute)
        client_socket.send(output)
    
    if command:
        while True:
            # show a simple prompt
            client_socket.send("<NETTOOL:#> ")
            # now we recieve until we see a line feed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            
            # send back the command output
            response = run_command(cmd_buffer)
            
            #send back the response
            client_socket.send(response)
            
def main():
    global listen, port, execute,command, upload_destination, target
    
    if not len(sys.argv[1:]):
        usage()
        
    #read the cli options
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",
                                  ["help", "listen", "execute","target","port","command","upload"])
    except getopt.GetoptError as e:
        print str(e)
        usage()
        
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
        
        # listen or just send data ?
        if not listen and len(target) and port > 0:
            buffer = '' # sys.stdin.read()
            client_sender(buffer)
            
        # we might drop a shell depending 
        # on our command
        if listen:
            server_loop()
main()







