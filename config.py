#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import ConfigParser
    cf = ConfigParser.RawConfigParser()
except:
    import configparser
    cf = configparser.RawConfigParser()


def defconfig(force):
    if (not cf.read('config')) or (force):
        cf.remove_section('CV')
        cf.add_section('CV')  # Convert values
        cf.set('CV', 'needpass', '')
        cf.set('CV', 'needpass0', 'Public,PU')
        cf.set('CV', 'needpass1', 'Private,PR')
        # Game types
        cf.set('CV', 'gametype', '')
        cf.set('CV', 'gametype0', 'Free for All,FFA')
        cf.set('CV', 'gametype1', 'Last Man Standing,LMS')
        cf.set('CV', 'gametype2', 'Free for All,FFA')
        cf.set('CV', 'gametype3', 'Team Deathmatch,TDM')
        cf.set('CV', 'gametype4', 'Team Survivor,TS')
        cf.set('CV', 'gametype5', 'Follow the Leader,FTL')
        cf.set('CV', 'gametype6', 'Capture & Hold,CNH')
        cf.set('CV', 'gametype7', 'Capture the Flag,CTF')
        cf.set('CV', 'gametype8', 'Bomb & Defuse,BM')
        cf.set('CV', 'gametype9', 'Jump Mode,J')
        cf.set('CV', 'gametype10', 'Freeze Tag,FT')
        cf.set('CV', 'gametype11', 'Gun Game,GUN')
        # Main win params  - MWP
        cf.remove_section('MWP')
        cf.add_section('MWP')
        # '<width>,<position>,<visible>,<align>,<title>
        cf.set('MWP', 'hostname',      '0,1,1,left,host')
        cf.set('MWP', 'modversion',    '8,2,1,right,ver.')
        cf.set('MWP', 'ping',          '4,3,1,right,ping')
        cf.set('MWP', 'clients',       '4,4,1,right,players')
        cf.set('MWP', 'bots',          '4,5,1,right,bots')
        cf.set('MWP', 'sv_maxclients', '4,6,1,right,maxPlayers')
        cf.set('MWP', 'gametype',      '4,7,1,right,gametype')
        cf.set('MWP', 'mapname',       '20,8,1,left,map')
        cf.write(open('config', 'w'))


def getdict(section, configfile, posvalue):
    cf.read(configfile)
    ret = dict(cf.items(section))
    if posvalue:
        for i in ret:
            ret[i] = ret[i].split(',')[posvalue-1]
    return ret
