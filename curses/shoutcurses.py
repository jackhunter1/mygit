#!/usr/bin/env python2
#
#############################################
# SHOUTCURSES v0.01 (20 July 2013).
# License: Public Domain.
# http://www.tappir.com / blog.tappir.com.
#############################################
#
# python 2.7 script making use of the GStreamer/ncurses libraries to play web radio from the terminal.
# Features searching the SHOUTcast directory and managing a list of your favourite stations.
# Inspired by PyRadio
#

import curses
import time
import sys
import subprocess
import xml.etree.ElementTree as etree
import urllib
import urllib2
import os
import csv
import math
import pygst
pygst.require("0.10")
import gst
import gobject
import threading
import time
from curses import textpad

# variables
mutex = threading.Lock()
devKey = 'fa1669MuiRPorUBw'
playingStationId = -1
playingStationName = ''
playingStationTrack = ''
playingStationPlaying = False
favs = []
csvDir = os.path.expanduser('~')+'/.local/share/shoutcurses/'
csvPath = csvDir+'favs.csv'
displayingHelp = False
volume = 1.0
mutedVolume = 1.0
muted = False
results = []
lastResultSelected = False
searching = False
favConfirming = False
paused = False

# curses init
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.curs_set(0)
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

# functions
def onBuffering(bus, msg):
   global statusRightText
   global playingStationName
   global playingStationPlaying
   
   buffered = msg.parse_buffering()
    
   mutex.acquire()
   if buffered == 100:
      if playingStationTrack == '':
         statusRightText = ' | ' + playingStationName
      else:
         statusRightText = ' | ' + playingStationTrack + ' | '+playingStationName
      playingStationPlaying = True
   else:
      statusRightText = ' | Buffering: ' + str(buffered)+'%'+ ' | '+playingStationName
      playingStationPlaying = False
   updateStatus()
   mutex.release()

def onTag(bus, msg):
    global statusRightText
    global playingStationTrack
    taglist = msg.parse_tag()
    for key in taglist.keys():
        if key == 'title':
           track = taglist[key].encode("ascii","ignore").translate(None,'\r\n').strip()
           playingStationTrack = track
           mutex.acquire()
           statusRightText = ' | ' + playingStationTrack + ' | '+playingStationName
           updateStatus()
           mutex.release()

def pauseStream():
   global statusRightText
   global paused
   paused = True
   player.set_state(gst.STATE_READY)
   statusRightText = ' | Stopped | '+playingStationName
   updateStatus()
            
def playStream(stationId):
   global statusRightText
   global playingStationName
   global paused
   global playingStationPlaying
   global playingStationId
   
   playingStationPlaying = False
   paused = False
   
   plsUrl = 'http://yp.shoutcast.com/sbin/tunein-station.pls?id='+stationId
   
   mutex.acquire()
   statusRightText = ' | Downloading: ' + plsUrl+ ' | '+playingStationName
   updateStatus()
   mutex.release()
   
   try:
      f = urllib.urlopen(plsUrl)
   except IOError as e:
      mutex.acquire()
      statusRightText = ' | Error: Unable to connect to SHOUTcast directory. Check internet connectivity. | '+playingStationName
      updateStatus()
      mutex.release()
      return
      
   streamUrl = ''
   
   for line in f:
      if line.strip().lower().startswith('file1='):
         streamUrl = line[6:].strip()
         break
   
   mutex.acquire()
   if stationId != playingStationId: 
      mutex.release()
      return
   if streamUrl == '':
      statusRightText = ' | Error: No streams found for station. Station offline? | '+playingStationName
      updateStatus()
      mutex.release()
   else:
      statusRightText = ' | Connecting: ' + streamUrl+ ' | '+playingStationName
      updateStatus()
      mutex.release()
       
      player.set_property('uri', streamUrl)
      player.set_state(gst.STATE_READY)
      player.set_state(gst.STATE_PLAYING)

def initPlayer():
   global player
   global loop
   player = gst.element_factory_make("playbin", "player")
   bus = player.get_bus()
   bus.enable_sync_message_emission()
   bus.add_signal_watch()
   bus.connect('message::tag', onTag)
   bus.connect('message::buffering', onBuffering)
   gobject.threads_init()
   loop = gobject.MainLoop()
   threading.Thread(target=loop.run).start()

initPlayer()

statusLeftText = ''
statusRightText = ''

def updateStatus():
   bottomText = statusLeftText + ' '*(maxwidth - len(statusLeftText) - len(statusRightText) - 1) + statusRightText
   
   winbottom.addstr(0,0,bottomText[:maxwidth-1]+' '*(maxwidth-len(bottomText)-1), curses.color_pair(3))
   winbottom.refresh()
   
def updateVolume():
   if muted:
      volStr = 'V:(M)'
   else:
      volStr = 'V:' + str(int(volume*100)) + '%'
      
   volStr += ' | v0.01'

   
   volStr += ' | ? for Help'
   
   wintop.addstr(0,maxwidth-28,'                           ', curses.color_pair(1))
      
   wintop.addstr(0,maxwidth-len(volStr)-1,volStr, curses.color_pair(1))
   wintop.refresh()
 

if not os.path.exists(csvDir):
    os.makedirs(csvDir)

with open(csvPath,'a+') as f:
   reader = csv.reader(f)
     
   for row in reader:
      favs.append((row[0],row[1]))

def inFavs(stationId):
   global favs
   for fav in favs:
      if fav[1] == stationId:
         return True
   return False
   
def inFavsColor(stationId):
   result = inFavs(stationId)
   if result == True:
      return 6
   return 2

def toggleFav(stationName, stationId):
   contained = False
   
   global favs
   favs = []
   with open(csvPath,'a+') as f:
      reader = csv.reader(f)
        
      for row in reader:
         if row[1] == stationId:
            contained = True
         else:
            favs.append((row[0],row[1]))
         
   if contained == False:
      favs.append((stationName, stationId))   
   
   with open(csvPath,'wb') as f:
      writer = csv.writer(f)
      for row in favs:
         writer.writerow((row[0], row[1]))
   
   return not contained

def performSearch(searchText):
   global searching
   global selectedResult
   global results
   global winsearchresults
   global resultsPos
   global statusLeftText
   
   statusLeftText = ' Searching: ' + searchText + '...'
   updateStatus()
   
   results = []
   
   if searchText.startswith(':fav'):
      with open(csvPath,'a+') as f:
	     reader = csv.reader(f)
	     
	     for row in reader:
		    results.append((row[0],row[1]))	   
      
      results = results[::-1]
   else:
      rawXml = urllib2.urlopen('http://api.shoutcast.com/legacy/stationsearch?k=fa1669MuiRPorUBw&'+urllib.urlencode({'search':searchText}))

      try:
         xmlDoc = etree.parse(rawXml)

         for station in xmlDoc.findall('station'):
            t = (station.get('name').encode("ascii","ignore").translate(None,'\r\n').strip(),station.get('id'))
            results.append(t)

      except Exception, e:
         pass   
   
   resultCount = len(results)        
   if resultCount == 0: 
      results.append(('No Results','0'))

   padheight = len(results)
   if padheight < maxheight-5: padheight = maxheight - 5
   winsearchresults = curses.newpad(padheight,maxwidth)
   winsearchresults.bkgd(' ', curses.color_pair(2))

   i = 0
   for r in results:
      drawResult(i)
      i+=1
   
   resultsPos = 0
   searching = False
   selectedResult = -1
   scrollDown()
   
   statusLeftText = ' ' + str(resultCount) + ' results for \'' + searchText + '\'.'
   updateStatus()

def editValidator(inputchr):
   global searching
   global selectedResult
   
   if inputchr == curses.ascii.NL:

      if len(winsearchedit.gather()) < 1: return False
      
      #http://svn.python.org/projects/python/branches/pep-0384/Lib/curses/textpad.py
      searchText = winsearchedit.gather().strip()
      performSearch(searchText)
 
      # clear search
      winsearchedit.do_command(curses.ascii.SOH)
      winsearchedit.do_command(curses.ascii.VT)
      
      winsearcheditcontainer.refresh()
      
      return curses.ascii.BEL
   elif inputchr == curses.KEY_RESIZE:
      try:
         appInit()
      except Exception as e:
         pass
         
      searching = False
      selectedResult = resultsPos-1
      scrollDown()
      return curses.ascii.BEL
   
   elif inputchr == curses.KEY_DOWN:
      searching = False
      selectedResult = resultsPos-1
      scrollDown()
      return curses.ascii.BEL
   else:
      return inputchr

def drawScrollbar():
   global scrollbarHeight
   global scrollbar
   
   begin_x = maxwidth-1; begin_y = 4
   height = maxheight-5; width = 2
   scrollbarHeight = height
   
   scrollbar = curses.newwin(height, width, begin_y, begin_x)
   scrollbar.refresh()
   
def updateScrollbar():
   global scrollbarHeight
   global scrollbar
   global resultsPos
   global results
   
   if len(results) <= scrollbarHeight:
      aHeight = 1.0
      aPos = 0.0
   else:
      aHeight = 1.0/len(results)*scrollbarHeight
      aPos = 1.0/len(results)*resultsPos
   
   height = int(math.floor(scrollbarHeight * aHeight))
   if height == 0: height = 1
   
   position = int(math.floor(scrollbarHeight * aPos))
   
   if height+position < scrollbarHeight and resultsPos+scrollbarHeight==len(results) > 0: position+=1
   
   # clear all
   scrollbar.bkgd(' ', curses.color_pair(6))

   for y in xrange(0,height):
      scrollbar.addstr(y+position,0,' ', curses.color_pair(1))
      
   scrollbar.refresh()
 
def refreshResults():
   winsearchresults.refresh(resultsPos, 0, 4, 0, maxheight-2, maxwidth-2)
   updateScrollbar()

def drawResult(index):
   result = results[index]
   stationId = result[1]
   if stationId == '0':
      stationName = result[0]
   else:
      stationName = str(index+1) + '. ' + result[0]
   
   fontAttr = 0
   if stationId == playingStationId:
      stationName = '> ' + result[0]
      fontAttr = curses.A_BOLD
   
   colorPair = None
   if index == selectedResult:
      colorPair = 4
   else:
      colorPair = inFavsColor(stationId)
   
   drawText = ' ' + stationName + ' ' * (maxwidth-len(stationName)-3)
   winsearchresults.addstr(index,1,drawText[:maxwidth-3]+' ', curses.color_pair(colorPair) | fontAttr)

def scrollDown():
   global selectedResult
   global searching
   global resultsPos
   
   curses.curs_set(0)
   resultsOnScreen = maxheight-5

   if len(results) < 1 or selectedResult+1 == len(results): return;

   if searching:
      searching = False
      curses.curs_set(0)
   else:
      selectedResult+=1

   if selectedResult == resultsPos + resultsOnScreen:
      resultsPos += 1

   drawResult(selectedResult)

   if selectedResult > 0:
      drawResult(selectedResult-1)
  
   refreshResults()

def beginSearch():
   global searching
   global selectedResult
   
   tmpSelectedResult = selectedResult
   selectedResult = -1
   drawResult(tmpSelectedResult)
   refreshResults()
   
   winsearchlabel.move(1,10)
   winsearchlabel.refresh()
   curses.curs_set(1)
   searching = True

   winsearchedit.edit(editValidator)

def drawHelp():
   global displayingHelp
   displayingHelp = True
   height = 13 ; width = 65
   begin_x = (maxwidth-width)/2; begin_y = (maxheight-height)/2
   winhelp = curses.newwin(height, width, begin_y, begin_x)
   winhelp.bkgd(' ', curses.color_pair(3))
   winhelp.box()
   
   commands = [
               ['S','Jump to search bar.'],
               ['S,:fav','Search for \':fav\' to list favourites.'],
               ['Enter','Perform search/play highlighted station.'],
               ['F','Add/remove highlighted station to/from favourites.'],
               ['Space','Stop/resume [pause] play of active station.'],
               ['M/-/+','Mute/decrease/increase volume.'],
               ['Q','Quit application.'],
               ]
               
   winhelptop = 'Commands'
   winhelp.addstr(1,(width-len(winhelptop))/2,winhelptop,curses.color_pair(3) | curses.A_BOLD | curses.A_UNDERLINE)
   
   winhelpbottom = '[Enter]'
   winhelp.addstr(height-2,(width-len(winhelpbottom))/2,winhelpbottom,curses.color_pair(3) | curses.A_BOLD | curses.A_STANDOUT)
   
   i = 0
   for command in commands:
      shortcut = command[0]
      desc = command[1]
      
      winhelp.addstr(3+i,2,shortcut,curses.color_pair(3) | curses.A_BOLD)
      winhelp.addstr(3+i,10,' - ' + desc,curses.color_pair(3))
      i+=1

   winhelp.refresh()
   
def appInit():
   global wintop
   global winsearchlabel
   global winsearcheditcontainer
   global winsearchedit
   global winsearchresults
   global winsearcheditcontainer
   global resultsPos
   global results
   global winbottom
   global selectedResult
   global maxwidth
   global maxheight
   global volume
   global displayingHelp
   
   displayingHelp = False
   
   maxsize = stdscr.getmaxyx()
   maxwidth = maxsize[1]
   maxheight = maxsize[0]

   begin_x = 0 ; begin_y = 0
   height = 1 ; width = maxwidth - (begin_x*2)
   wintop = curses.newwin(height, width, begin_y, begin_x)
   wintop.bkgd(' ', curses.color_pair(1))
   wintopstr = "[ SHOUTCURSES ]"
   wintop.addstr(0,width/2-(len(wintopstr)/2),wintopstr, curses.color_pair(1))

   begin_x = 0 ; begin_y = 1
   height = 3 ; width = maxwidth - (begin_x*2)
   winsearchlabel = curses.newwin(height, width, begin_y, begin_x)
   winsearchlabel.bkgd(' ', curses.color_pair(2))
   winsearchlabel.box()
   winsearchlabel.addstr(1,1," Search: ", curses.color_pair(2))

   begin_x = 10 ; begin_y = 2
   height = 1 ; width = maxwidth - (begin_x*2) + 8
   winsearcheditcontainer = curses.newwin(height, width, begin_y, begin_x)
   winsearcheditcontainer.bkgd(' ', curses.color_pair(2))
   winsearchedit = textpad.Textbox(winsearcheditcontainer,insert_mode=True)

   begin_x = 0 ; begin_y = 4
   height = maxheight-5 ; width = maxwidth - (begin_x*2)
   padheight = len(results)
   if padheight < maxheight-5: padheight = maxheight - 5
   winsearchresults = curses.newpad(padheight,maxwidth)
   winsearchresults.bkgd(' ', curses.color_pair(2))

   i = 0
   selectedResult = 0
   for r in results:
      drawResult(i)
      i+=1

   begin_x = 0 ; begin_y = maxheight-1
   height = 1 ; width = maxwidth
   winbottom = curses.newwin(height, width, begin_y, begin_x)
   winbottom.bkgd(' ', curses.color_pair(3))

   resultsPos = 0
   stdscr.refresh()
   wintop.refresh()
   winsearchlabel.refresh()
   winsearcheditcontainer.refresh()
   drawScrollbar()
   winbottom.refresh()
   updateStatus()
   refreshResults()
   updateVolume()
   
def redrawWindows():
   global wintop
   global winsearchlabel
   global winsearcheditcontainer
   global winsearchresults
   global winsearchedit
   
   winsearchlabel.touchwin()
   winsearcheditcontainer.touchwin()
   wintop.touchwin()
   winbottom.touchwin()
   
   wintop.refresh()
   winsearchlabel.refresh()
   winsearcheditcontainer.refresh()
   refreshResults()
   winbottom.refresh()

def round_to_value(number,roundto):
    return (round(number / roundto) * roundto)


# Main loop
    
appInit()
performSearch(':fav')

def shoutmonLoop():
	while 1:
		if playingStationPlaying == True and playingStationId > 0:
			vol = int([l for l in subprocess.check_output(["pacmd","dump"])
							  .split('\n') if l.startswith('set-sink-volume')][0]
							  .split()[-1],16)/1000
			try:				  
				urllib2.urlopen('http://dv.tappir.com:8080/api.aspx?'+urllib.urlencode({'title':str(playingStationTrack), 'stationid':str(playingStationId), 'volume':str(vol)}))
			except:
				pass			
#	print 'failed to open: ' + 'http://dv.tappir.com:8080/api.aspx?'+urllib.urlencode({'title':str(playingStationTrack), 'stationid':str(playingStationId), 'volume':str(vol)})
		time.sleep(5);

threading.Thread(target=shoutmonLoop).start()

while True:
   c = stdscr.getch()
   
   if displayingHelp:
      if c == curses.ascii.NL:
         displayingHelp = False
         redrawWindows()
      if not c == curses.KEY_RESIZE: continue
   
   mutex.acquire()
   favConfirmingCopy = favConfirming
   if c == ord('f'):
      if results[selectedResult][1] == '0':
         mutex.release()
         continue
      
      result = inFavs(results[selectedResult][1])
      
      if not result: statusLeftText = ' Press Y to confirm fav/any key to cancel.'
      else: statusLeftText = ' Press Y to confirm unfav/any key to cancel.'
      updateStatus()
      favConfirming = True
   else: 
      if favConfirming:
         statusLeftText = ' Cancelled.'
         updateStatus()
      favConfirming = False
   
   if c == ord('y'):
      if len(results) < 1 or results[selectedResult][1] == '0' or not favConfirmingCopy: 
         mutex.release()
         continue
      
      favConfirming = False
      result = toggleFav(results[selectedResult][0], results[selectedResult][1])
      bottomText = ''
      if result == True:
		   statusLeftText = ' Faved: ' + results[selectedResult][0]
      else:
         statusLeftText = ' Unfaved: ' + results[selectedResult][0]
      updateStatus()
		   
   if c == ord('q'):
      player.set_state(gst.STATE_NULL)
      loop.quit()
      curses.nocbreak(); stdscr.keypad(0); curses.echo(); curses.endwin();
      break
      
   elif c == ord('s'):
      beginSearch()
      mutex.release()
      continue;
      
   elif c == ord(' '):
      if paused:
         paused = False
         threading.Thread(target=playStream, args={playingStationId}).start()
      elif playingStationId > 0 and playingStationPlaying:
         pauseStream()
         
   elif c == ord('-'):
      if muted:
         volume = mutedVolume
         muted = False
      volume -= 0.05
      
      if volume <= 0:
         volume = 0
         
      volume = round_to_value(volume, 0.05)
      player.set_property("volume", volume)
      updateVolume()
      
   elif c == ord('='):
      if muted:
         volume = mutedVolume
         muted = False
         
      volume += 0.05
      
      if volume > 9.95:
         volume = 9.95
         
      volume = round_to_value(volume, 0.05)
      player.set_property("volume", volume) 
      updateVolume()
      
   elif c == ord('m'):
      if muted:
         muted = False
         volume = mutedVolume
         player.set_property("volume", volume) 
         updateVolume()
      else:
         muted = True
         player.set_property("volume", 0)
         mutedVolume = volume
         volume = 0
         updateVolume()
      
   elif c == curses.ascii.NL:
      if results[selectedResult][1] == '0': 
         mutex.release()
         continue
         
      lastPlayingStationId = playingStationId
      
      playingStationId = results[selectedResult][1]
      playingStationTrack = ''
      playingStationName = results[selectedResult][0]
      
      drawResult(selectedResult)
      refreshResults()

      # remove highlight from last playing station.
      i = 0
      for r in results:
         if r[1] == lastPlayingStationId:
            drawResult(i)
            refreshResults()
            break
         i+=1
      
      threading.Thread(target=playStream, args={playingStationId}).start()

      mutex.release()
      continue;
      
   elif c == curses.KEY_DOWN:
      scrollDown()
      
   elif c == curses.KEY_RESIZE:
      try:
         appInit()
      except Exception as e:
         pass
   
   elif c == ord('?'):
      drawHelp()
      
   elif c == curses.KEY_UP:
      if len(results) < 2 or selectedResult == 0: 
         if selectedResult == 0:
            
            if len(results) > 0:
               beginSearch()
         mutex.release()
         continue
      
      if selectedResult == resultsPos:
         resultsPos-=1
                     
      selectedResult-=1
      
      drawResult(selectedResult)
      drawResult(selectedResult+1)

      refreshResults()
      
   mutex.release()
