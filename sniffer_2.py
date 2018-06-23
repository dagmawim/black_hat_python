import socket
import os
import struct
from ctypes import *

host = "192.168.148.131"

class IP(Structure):
    _fields_ = [
        ("ihl",          c_ubyte, 4),
        ("version",      c_ubyte, 4),
        ("tos",          c_ubyte),
        ("len",          c_ushort),
        ("id",           c_ushort),
        ("offset",       c_short),
        ("ttl",          c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum",          c_ushort),
        ("src",          c_uint32),
        ("dst",          c_uint32)
    ]
    
    
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        #map protocol constants
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        
        #human readable IP adresses
        k = struct.pack("q", self.src)
        self.src_address = socket.inet_ntoa(struct.pack("@I",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I",self.dst))
        
        #human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)
    
if os.name == "nt":
    socket_protocol = socket.IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

#include ip header in capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)        

if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
try:
    while True:
        #read in a packet
        raw_buffer = sniffer.recvfrom(65535)[0]
        
        #create an IP header from first 20 bytes of buffer
        ip_header = IP(raw_buffer)
        
        #print protocol and address
        print "Protocol: %s %s -> %s" %(ip_header.protocol,ip_header.src_address,
                                        ip_header.dst_address)
        
    
except KeyboardInterrupt:
    #if windows set up IOCTL to turn off promiscous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)    
    