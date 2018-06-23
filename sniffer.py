import socket
import os

host = "192.168.148.130"

if os.name == "nt":
    socket_protocol = socket.IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

#include ip header in capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

#if windows set up IOCTL for promiscous mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

#read in a single packet
print sniffer.recvfrom(65565)

#if windows set up IOCTL to turn off promiscous mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)



    