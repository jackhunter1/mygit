#!/usr/bin/env python
import curses
#from curses.wrapper import wrapper
import re


def addstr_colorized(win, y, x, s):
	colors = {'^1': 1, '^2': 2, '^3':3, '^4':4, '^5':5, '^6':6, '^7':7, '^8':8}
	win.move(y, x)
	pattern = r'(\^\d){,1}'#r'({0:s})'.format('|'.join(r'\b{0:s}\b'.format(word) for word in colors.keys()))
	s = re.split(pattern, s)
	col = 7
	for s in s:
		if colors.get(s, 0):
			col = colors.get(s, 0)
		if not colors.get(s, 0):
			win.addstr(s, curses.color_pair(col))


def main(stdscr):
	bkg = 8
	curses.init_pair(1, curses.COLOR_RED, bkg)
	curses.init_pair(2, curses.COLOR_GREEN, bkg)
	curses.init_pair(3, curses.COLOR_YELLOW, bkg)
	curses.init_pair(4, curses.COLOR_BLUE, bkg)
	curses.init_pair(5, curses.COLOR_CYAN, bkg)
	curses.init_pair(6, curses.COLOR_MAGENTA, bkg)
	curses.init_pair(7, curses.COLOR_WHITE, bkg)
	curses.init_pair(8, curses.COLOR_BLACK, bkg)

	addstr_colorized(stdscr, 4, 0, "^2-=^6Ur^7T4 ^4CTF East=-^3|^2Jump ^5Server")
	stdscr.refresh()
	stdscr.getch()


curses.wrapper(main)
