from scapy.all import *

def p_callback(packet):
    print packet.show()

sniff(prn=p_callback, count=1)