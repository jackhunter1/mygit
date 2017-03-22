#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import sys
import time
import re
from multiprocessing.dummy import Pool as ThreadPool

PY_V = sys.version_info.major


def recievedata(server, command, buffsize):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(command, server)
    ping = 0
    resp = None
    resplist = []
    while True:
        TS = time.time()
        try:
            resp = sock.recv(buffsize)
        except:
            break
        if not resp:
            break
        else:
            resplist.append(resp)
            ping = int((time.time()-TS)*1000)
    sock.close()
    return resplist, str(ping)


def getserverslist():
    master_ip = 'master.urbanterror.info'
    master_port = 27900
    resplist, ping = recievedata((master_ip, master_port), b'\xff\xff\xff\xffgetservers 68 empty full demo', 1395)
    slist = []
    for packet in resplist:
        index = 22  # OOB bytes + getserversResponse = 22 bytes
        # Iterate over the 7 byte fields in the packet
        while True:
            if index+7 >= len(packet):
                break
            ip = socket.inet_ntoa(packet[index+1:index+5])
            if PY_V == 3:  # Major python release
                port = 256*(packet[index+5]) + (packet[index+6])
            else:
                port = 256*ord(packet[index+5]) + ord(packet[index+6])
            slist.append((ip, port))
            index += 7
    return slist


def getserverinfo(server):
    fullinfo = []
    servinfolist, ping = recievedata(server, b'\xff\xff\xff\xffgetinfo', 1024)
    if not servinfolist:
        return ['nothing']
    if PY_V == 3:  # Major python release
        servinfolist = servinfolist[0][17:].decode('utf-8', errors='replace').split('\\')[1:]
    else:
        servinfolist = servinfolist[0].split('\\')[1:]
    hostname_nocc = servinfolist[servinfolist.index('hostname')+1].strip()
    hostname_nocc = re.sub(r'[^\x00-\x7f]', r'.', hostname_nocc)  # Replace hex symbols
    servinfolist[servinfolist.index('hostname')+1] = hostname_nocc
    mapname = servinfolist[servinfolist.index('mapname')+1].strip()
    mapname = re.sub(r'(\^\d){,1}ut\d{,2}_', '', mapname)
    hostname_nocc = re.sub(r'(\^\d){,1}', '', hostname_nocc)  # Replace q3 color codes
    servinfolist[servinfolist.index('mapname')+1] = mapname
    try:
        servinfolist.index('bots')
    except:
        servinfolist.extend(['bots', '---'])
    servinfolist.extend(['hostname_nocc', hostname_nocc.upper()])
    servinfolist.extend(['ip_port', server, 'ping', ping.rjust(3, '0')])
    for i in servinfolist[::2]: servinfolist[servinfolist.index(i)] = i.lower();
    fullinfo.append(servinfolist)
    resplist, ping = recievedata(server, b'\xff\xff\xff\xffgetstatus', 2048)
    if not resplist:
        return ['nothing']
    playerlist = []
    if PY_V == 3:  # Major python release
        resplist = resplist[0][19:].decode('utf-8', errors='replace')
    else:
        resplist = resplist[0][19:]
    statlist = resplist.split('\n')[0].split('\\')[1:]
    for i in statlist[::2]: statlist[statlist.index(i)] = i.lower();
    for x in resplist.split('\n')[1:-1]:
        plist = []
        plist.extend(x.split('"')[0].split(' ')[:2])
        plist.append(x.split('"')[1])
        plist = tuple(plist)
        playerlist.append(plist)
    fullinfo.append(statlist)
    fullinfo.append(playerlist)
    return fullinfo


def getserversdata():
    serverslist = getserverslist()
    datalist = []
    pool = ThreadPool(200)
    datalist = pool.map(getserverinfo, serverslist)
    pool.close()
    pool.join()
    while True:
        try:
            datalist.remove(['nothing'])
        except:
            break
    return datalist
