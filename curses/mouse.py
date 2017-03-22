#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses

def main(scr):
     curses.mousemask(curses.ALL_MOUSE_EVENTS)
     key=0
     while key!=27:
         key=scr.getch()
         scr.erase()
         if key==curses.KEY_MOUSE:
             scr.addstr(0,0,str(curses.getmouse()))
         else:
             scr.addstr(0,0,str(key))
         scr.refresh()

if __name__=='__main__':
     curses.wrapper(main)
