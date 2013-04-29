#!/usr/bin/env python

import socket, sys
from struct import *

class bcolors:
    HEADER = '\033[97m'
    OKBLUE = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
 
#Convert a string of 6 characters of ethernet address into a dash separated hex string
def eth_addr (a) :
  b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
  return b

def printd (d,ds):
    if ds > 0:
        print bcolors.WARNING + '\nData Size: ' + str(len(d.encode("hex")))
        if ds <= 512:
            print 'Data: ' + d.encode("hex") + bcolors.ENDC
        else:
            print 'Data: ' + d.encode("hex")[:512] + '.....' + bcolors.ENDC

def tcp(t,packet):
    tcp_header = packet[t:t+20]
 
    #now unpack them :)
    tcph = unpack('!HHLLBBHHH' , tcp_header)
             
    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
             
    print bcolors.OKGREEN + '\nProtocol: TCP\nSource Port: ' + str(source_port) + '\nDest Port: ' + str(dest_port) + '\nSequence Number: ' + str(sequence) + '\nAcknowledgement: ' + str(acknowledgement) + '\nTCP header length: ' + str(tcph_length) + bcolors.ENDC
             
    h_size = t + tcph_length * 4
    data_size = len(packet) - h_size
            
    #get data from the packet
    data = packet[h_size:]
    printd(data,data_size)             

def icmp(u,packet):
    icmph_length = 4
    icmp_header = packet[u:u+4]
 
    #now unpack them :)
    icmph = unpack('!BBH' , icmp_header)
            
    icmp_type = icmph[0]
    code = icmph[1]
    checksum = icmph[2]
             
    print bcolors.OKGREEN + '\nProtocol: ICMP\nType: ' + str(icmp_type) + '\nCode: ' + str(code) + '\nChecksum: ' + str(checksum) + bcolors.ENDC
             
    h_size = u + icmph_length
    data_size = len(packet) - h_size
             
    #get data from the packet
    data = packet[h_size:]
    printd(data,data_size)

def udp(u,packet):
    udph_length = 8
    udp_header = packet[u:u+8]
 
    #now unpack them :)
    udph = unpack('!HHHH' , udp_header)
             
    source_port = udph[0]
    dest_port = udph[1]
    length = udph[2]
    checksum = udph[3]
            
    print bcolors.OKGREEN + '\nProtocol: UDP\nSource Port: ' + str(source_port) + '\nDest Port: ' + str(dest_port) + '\nLength: ' + str(length) + '\nChecksum: ' + str(checksum) + bcolors.ENDC
             
    h_size = u + udph_length
    data_size = len(packet) - h_size
             
    #get data from the packet
    data = packet[h_size:]
    printd(data,data_size)    


#create a AF_PACKET type raw socket (thats basically packet level)
#define ETH_P_ALL    0x0003          /* Every packet (be careful!!!) */
try:
    s = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
except socket.error , msg:
    print bcolors.FAIL + 'Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1] + bcolors.ENDC
    sys.exit()
 
# receive a packet
try:
    while True:
        packet = s.recvfrom(65565)
     
        #packet string from tuple
        packet = packet[0]
     
        #parse ethernet header
        eth_length = 14
     
        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH' , eth_header)
        eth_protocol = socket.ntohs(eth[2])

        ip_header = packet[eth_length:20+eth_length]
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
        protocol = iph[6]
        if len(sys.argv) > 1:
            if any( [ all( [sys.argv[1] == 'TCP', str(protocol) != '6'] ),
                    all( [sys.argv[1] == 'UDP', str(protocol) != '17'] ),
                    all( [sys.argv[1] == 'ICMP', str(protocol) != '1'] ) ] ):
                continue
            elif sys.argv[1] == 'help':
                print bcolors.FAIL + "Usage: python snifv2.py <protocol> <IP>" + bcolors.ENDC
                sys.exit()

        #Parse IP packets, IP Protocol number = 8
        if eth_protocol == 8 :

            version_ihl = iph[0]
            version = version_ihl >> 4
            ihl = version_ihl & 0xF
 
            iph_length = ihl * 4
  
            ttl = iph[5]
            s_addr = socket.inet_ntoa(iph[8]);
            d_addr = socket.inet_ntoa(iph[9]);
            if len(sys.argv) == 3:
                if sys.argv[2] == str(s_addr) or str(d_addr):
                    print bcolors.HEADER + 'Destination MAC: ' + eth_addr(packet[0:6]) + '\nSource MAC: ' + eth_addr(packet[6:12]) + bcolors.ENDC
                    print bcolors.OKBLUE + '\nProtocol: IP\nVersion: ' + str(version) + '\nIP Header Length: ' + str(ihl) + '\nTTL: ' + str(ttl) + '\nSource Address: ' + str(s_addr) + '\nDestination Address: ' + str(d_addr) + bcolors.ENDC
                else:
                    continue
            else:
                print bcolors.HEADER + 'Destination MAC: ' + eth_addr(packet[0:6]) + '\nSource MAC: ' + eth_addr(packet[6:12]) + bcolors.ENDC
                print bcolors.OKBLUE + '\nProtocol: IP\nVersion: ' + str(version) + '\nIP Header Length: ' + str(ihl) + '\nTTL: ' + str(ttl) + '\nSource Address: ' + str(s_addr) + '\nDestination Address: ' + str(d_addr) + bcolors.ENDC

            #TCP protocol
            if protocol == 6 :
                tcp(iph_length+eth_length,packet)
 
            #ICMP Packets
            elif protocol == 1 :
                icmp(iph_length+eth_length,packet)      
 
            #UDP packets
            elif protocol == 17 :
                udp(iph_length+eth_length,packet)

            #some other IP packet like IGMP
            else :
                print '\nProtocol other than TCP/UDP/ICMP'
             
            print '\n'+'-_'*60+'\n'
except KeyboardInterrupt:
    print bcolors.FAIL + "\nCaught keyboard interrupt, exiting." + bcolors.ENDC
    sys.exit(0)
