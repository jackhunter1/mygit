#!/usr/bin/env python
#
# $Id$
#
# (n)curses exerciser in Python, an interactive test for the curses
# module. Currently, only the panel demos are ported.

import curses
from curses import panel

def wGetchar(win = None):
	if win is None: win = stdscr
	return win.getch()

def Getchar():
	wGetchar()

#
# Panels tester
#
def wait_a_while():
	if nap_msec == 1:
		Getchar()
	else:
		curses.napms(nap_msec)

def saywhat(text):
	stdscr.move(curses.LINES - 1, 0)
	stdscr.clrtoeol()
	stdscr.addstr(text)

def mkpanel(color, rows, cols, tly, tlx):
	win = curses.newwin(rows, cols, tly, tlx)
	pan = panel.new_panel(win)
	if curses.has_colors():
		if color == curses.COLOR_BLUE:
			fg = curses.COLOR_WHITE
		else:
			fg = curses.COLOR_BLACK
		bg = color
		curses.init_pair(color, fg, bg)
		win.bkgdset(ord(' '), curses.color_pair(color))
	else:
		win.bkgdset(ord(' '), curses.A_BOLD)
 
	return pan

def pflush():
	panel.update_panels()
	curses.doupdate()

def fill_panel(pan):
	win = pan.window()
	num = pan.userptr()[1]

	win.move(1, 1)
	win.addstr("-pan%c-" % num)
	win.clrtoeol()
	win.box()

	maxy, maxx = win.getmaxyx()
	for y in range(2, maxy - 1):
		for x in range(1, maxx - 1):
			win.move(y, x)
			win.addch(num)

def demo_panels(win):
	global stdscr, nap_msec, mod
	stdscr = win
	nap_msec = 1
	mod = ["test", "TEST", "(**)", "*()*", "<-->", "LAST"]
	panels_dict = {} 
	stdscr.refresh()

	for y in range(0, curses.LINES - 1):
		for x in range(0, curses.COLS):
			stdscr.addstr("%d" % ((y + x) % 10))
	for y in range(0, 1):
		p1 = mkpanel(curses.COLOR_RED,
					 curses.LINES // 2 - 2,
					 curses.COLS // 8 + 1,
					 0,
					 0)
		p1.set_userptr("p1")
		panels_dict['1'] = p1

		p2 = mkpanel(curses.COLOR_GREEN,
					 curses.LINES // 2 + 1,
					 curses.COLS // 7,
					 curses.LINES // 4,
					 curses.COLS // 10)
		p2.set_userptr("p2")
		panels_dict['2'] = p2

		p3 = mkpanel(curses.COLOR_YELLOW,
					 curses.LINES // 4,
					 curses.COLS // 10,
					 curses.LINES // 2,
					 curses.COLS // 9)
		p3.set_userptr("p3")
		panels_dict['3'] = p3

		p4 = mkpanel(curses.COLOR_BLUE,
					 curses.LINES // 2 - 2,
					 curses.COLS // 8,
					 curses.LINES // 2 - 2,
					 curses.COLS // 3)
		p4.set_userptr("p4")
		panels_dict['4'] = p4

		p5 = mkpanel(curses.COLOR_MAGENTA,
					 curses.LINES // 2 - 2,
					 curses.COLS // 8,
					 curses.LINES // 2,
					 curses.COLS // 2 - 2)
		p5.set_userptr("p5")
		panels_dict['5'] = p5
		
		for i in panels_dict.values():
			fill_panel(i)
			i.show()
		pflush()
		wait_a_while()
		
		panels_dict['3'].top()
		pflush()
		wait_a_while()
		
		panels_dict['2'].hide()
		pflush()
		wait_a_while()

#
# one fine day there'll be the menu at this place
#
curses.wrapper(demo_panels)
