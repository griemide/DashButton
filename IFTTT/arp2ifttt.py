# Michael Gries, 2006
# based on arp_to_ifttt.py by Aaron Bell on https://gist.github.com
# modified: 2016-09-09 (adapted to my first Amazon Dash Botton 'Cottonelle'

import socket
import struct
import binascii
import time
import json
import urllib2

# Set IFTTT key 
ifttt_key = 'kg6PLDrSBNSeUIk_Uuk72rYPfPtMcj2Vc4JuuUqZXj2'
# Set these up at https://ifttt.com/maker or https://ifttt.com/maker
# ifttt_url_test = 'https://maker.ifttt.com/trigger/test/with/key/' + ifttt_key
# Note: https currently not supported on Arduino Yun 
ifttt_url_test = 'http://maker.ifttt.com/trigger/test/with/key/' + ifttt_key
ifttt_url_iPad = 'http://maker.ifttt.com/trigger/test/with/key/' + ifttt_key
# IFTT test reference https://maker.ifttt.com/trigger/test/with/key/kg6PLDrSBNSeUIk_Uuk72rYPfPtMcj2Vc4JuuUqZXj2

# assign known MAC addresses to nicknames
macs = {
    '54675179607d' : 'ConnectBox',
    '5ccf7f0f791f' : 'af104-pws',
    '90a2daf20276' : 'ArduinoYun',
    'cc3d82de7de4' : 'BBMAG2083',
    '88cb87e0a43a' : 'iPad-Mini',
    '50f5da6c24b1' : 'DB-Cottonelle'
}

# Trigger a IFTTT URL. Body includes JSON with timestamp values.
def trigger_url(url):
    data = '{ "value1" : "' + time.strftime("%Y-%m-%d") + '", "value2" : "' + time.strftime("%H:%M") + '" }'
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    return response

def record_test():
    print 'triggering test event, response: ' + trigger_url(ifttt_url_test)

def record_iPad():
    print 'triggering iPad event, response: ' + trigger_url(ifttt_url_iPad)

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

while True:
    packet = rawSocket.recvfrom(2048)
    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)
    # skip non-ARP packets
    ethertype = ethernet_detailed[2]
    if ethertype != '\x08\x06':
        continue
    # read out data
    arp_header = packet[0][14:42]
    arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
    source_mac = binascii.hexlify(arp_detailed[5])
    source_ip = socket.inet_ntoa(arp_detailed[6])
    dest_ip = socket.inet_ntoa(arp_detailed[8])
    if source_mac in macs:
        print "ARP from " + macs[source_mac] + " with IP " + source_ip
        if macs[source_mac] == 'DB-Cottonelle':
            record_test()
        if macs[source_mac] == 'iPad-Mini':
            record_iPad()
    else:
        print "Unknown MAC " + source_mac + " from IP " + source_ip

        
