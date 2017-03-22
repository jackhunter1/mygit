#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import curses

class mainwin:
	def __init__(self, scr):
		Y,X = scr.getmaxyx()
		self.Y = Y
		self.X = X
		self.w = curses.newwin(self.Y, self.X, 0, 0)
	def win(self):
		self.tw = self.w.subwin(self.Y-10, self.X-10, 0,0)
		Y,X = self.tw.getmaxyx()
		self.tw.box()
		for j in range(Y-2):
			self.tw.addstr(j+1,1,'!'*(X-2))
		self.tw.refresh()
	def delw(self):
		self.tw.erase()
		self.w.refresh()
def main(stdscr):
	if curses.has_colors():
		#curses.init_pair(0, curses.COLOR_BLACK, 0)
		curses.init_pair(1, curses.COLOR_RED, 0)
		curses.init_pair(2, curses.COLOR_GREEN, 0)
		curses.init_pair(3, curses.COLOR_YELLOW, 0)
		curses.init_pair(4, curses.COLOR_BLUE, 0)
		curses.init_pair(5, curses.COLOR_CYAN, 0)
		curses.init_pair(6, curses.COLOR_MAGENTA, 0)
		curses.init_pair(7, curses.COLOR_WHITE, 0)
		curses.init_pair(8, curses.COLOR_BLACK, 0)
		stdscr.clear()
		mw = mainwin(stdscr)
		while True:
			key = stdscr.getch()
			if key == 27:
				break
			if key in [103,71]:
				mw.win()
			if key in [68,100]:
				mw.delw()

if __name__ == '__main__':
 curses.wrapper(main)
