#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Base python modules
import curses
import re
import warnings
from curses import panel
from math import *
# Browser modules
import q3socket
import config
warnings.filterwarnings("ignore", category=FutureWarning)
# Just add one comment


class DataStruct:
    def __init__(self, scr):
        Y, X = scr.getmaxyx()
        self.Y = Y
        self.X = X
        self.dictCV = config.getdict('CV', 'config', 0)  # Dict convert values
        self.dictMWP_width = config.getdict('MWP', 'config', 1)  # Dict width coloumns
        self.dictMWP_pos = config.getdict('MWP', 'config', 2)  # Dict coloumn position
        self.dictMWP_vis = config.getdict('MWP', 'config', 3)  # Dict visible coloumn
        self.dictMWP_align = config.getdict('MWP', 'config', 4)
        self.dictMWP_title = config.getdict('MWP', 'config', 5)
        self.dictMWP_width['hostname'] = str(self.X-(sum([int(self.dictMWP_width[i])*int(self.dictMWP_vis[i]) for i in self.dictMWP_width])+9))
        self.typelist = 'all'
        self.strpos = 1
        self.rangestart = 0
        self.datalist = q3socket.getserversdata()


def resultstring(ds, st, elemdl, revc):  # ds - datastruct, st - panel, elemdl- element datalist, revc - reverse color
    colors = {'^0': 200, '^1': 201, '^2': 202, '^3': 203, '^4': 204, '^5': 205, '^6': 206, '^7': 207, '^8': 208, '^9': 209}
    pattern = r'(\^\d)+'
    resstr = ''
    for i in sorted(ds.dictMWP_pos.items(), key=lambda v: v[1], reverse=False):
        colwidth = int(ds.dictMWP_width[i[0]])
        if i[0] in ds.dictCV:
            resstr = ds.dictCV[i[0]+elemdl[elemdl.index(i[0])+1]].split(',')[1]
        else:
            resstr = elemdl[elemdl.index(i[0])+1]
        col = 207  # White color
        if ds.dictMWP_align[i[0]] == 'right':
            try:
                l = len(elemdl[elemdl.index(i[0]+'_nocc')+1])
            except:
                l = len(resstr)
            st.window().addstr(' '*(colwidth-l), curses.color_pair(col+revc))
        resstr = re.split(pattern, resstr)
        for resstr in resstr:
            if colors.get(resstr, 0):
                col = colors.get(resstr, 0)
            else:
                colwidth -= len(resstr)
                if colwidth == 0:
                    st.window().addstr(resstr, curses.color_pair(col+revc))
                    break
                elif colwidth < 0:
                    st.window().addstr(resstr[:colwidth], curses.color_pair(col+revc))
                    break
                else:
                    st.window().addstr(resstr, curses.color_pair(col+revc))
        if ds.dictMWP_align[i[0]] == 'left':
            st.window().addstr(' '*colwidth, curses.color_pair(col+revc))
        st.window().addch(curses.ACS_VLINE)


def refreshmainwin(ds, st):
    Y, X = st.window().getmaxyx()
    if ds.strpos == 0: ds.strpos = 1; return;
    if ds.strpos == len(ds.datalist)+1: ds.strpos = len(ds.datalist); return;
    if ds.strpos == ds.rangestart: ds.rangestart -= 1;
    if ds.strpos == ds.rangestart+Y-1: ds.rangestart += 1;
    i = 1
    for s in ds.datalist[ds.rangestart: ds.rangestart+Y-2]:
        st.window().move(i, 1)
        if i == ds.strpos-ds.rangestart:
            resultstring(ds, st, s[0], 10)
        else:
            resultstring(ds, st, s[0], 0)
        i += 1
    refreshpanels()


def refreshpanels():
    panel.update_panels()
    curses.doupdate()


def makepanel(rows, cols, tly, tlx, name, bkg):
    win = curses.newwin(rows, cols, tly, tlx)
    pan = panel.new_panel(win)
    win.bkgdset(ord(' '), curses.color_pair(bkg))
    win.box()
    win.addstr(0, 1, name)
    return pan


def sortbycolumn(col, ds, st):
    ds.datalist.sort(key=lambda i: i[0][i[0].index(col)+1])
    refreshmainwin(ds, st)


def keyloop(stdscr):
    stdscr.clear()
    pan_d = {}
    Y, X = stdscr.getmaxyx()
    pan_d['MWT'] = makepanel(3, X, 0, 0, '|All servers|', 207)
    pan_d['MW'] = makepanel(Y-4, X, 2, 0, '', 207)  # Servers table panel
    refreshpanels()
    ds = DataStruct(stdscr)
    refreshmainwin(ds, pan_d['MW'])
    while True:
        x = stdscr.getch()
        if (x == 27) or (x in [113, 81]):  # Press ESC or Q/q quit
            break
        elif x in [103, 71]:  # Press G/g - update servers list
            ds.datalist = q3socket.getserversdata()
            ds.strpos = 1
            ds.rangestart = 0
            refreshmainwin(ds, pan_d['MW'])
        elif x in [105, 73]:  # Press I/i - info panel
            ds.infopanel()
        elif x in [115]:
            sortbycolumn('ping', ds, pan_d['MW'])
        elif x == curses.KEY_UP:
            ds.strpos -= 1
            refreshmainwin(ds, pan_d['MW'])
        elif x == curses.KEY_DOWN:
            ds.strpos += 1
            refreshmainwin(ds, pan_d['MW'])
        elif x == 10:
            pan_d['MW'].window().hline(ds.Y-1, 1, curses.ACS_HLINE, ds.X-2)
            pan_d['MW'].window().addstr(ds.Y-1, 1, ds.datalist[ds.strpos-1][0][ds.datalist[ds.strpos-1][0].index('hostname')+1])
            refreshpanels()
        elif x == curses.KEY_MOUSE:
            mid, mx, my, mz, bstate = curses.getmouse()
            refreshpanels()


def main(stdscr):
    # If color, then initialize the color pairs
    if curses.has_colors():
        bkg = 240
        curses.start_color()
        curses.init_pair(200,  curses.COLOR_BLACK, bkg)
        curses.init_pair(201,  curses.COLOR_RED, bkg)
        curses.init_pair(202,  curses.COLOR_GREEN, bkg)
        curses.init_pair(203, 11, bkg)  # Curses.COLOR_YELLOW
        curses.init_pair(204,  curses.COLOR_BLUE, bkg)
        curses.init_pair(205,  curses.COLOR_CYAN, bkg)
        curses.init_pair(206,  curses.COLOR_MAGENTA, bkg)
        curses.init_pair(207,  curses.COLOR_WHITE, bkg)
        curses.init_pair(208,  203, bkg)
        curses.init_pair(209,  8, bkg)
        curses.init_pair(210, bkg, curses.COLOR_BLACK)
        curses.init_pair(211,  bkg, curses.COLOR_RED)
        curses.init_pair(212, bkg, curses.COLOR_GREEN)
        curses.init_pair(213, bkg, 11)
        curses.init_pair(214, bkg, curses.COLOR_BLUE)
        curses.init_pair(215, bkg, curses.COLOR_CYAN)
        curses.init_pair(216, bkg, curses.COLOR_MAGENTA)
        curses.init_pair(217, bkg, curses.COLOR_WHITE)
        curses.init_pair(218, bkg, 203)
        curses.init_pair(219, bkg, 8)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
    config.defconfig(False)
    keyloop(stdscr)

if __name__ == '__main__':
    curses.wrapper(main)
