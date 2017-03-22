#!/usr/bin/env python
import curses, subprocess
from math import *



screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
#curses.mousemask(curses.BUTTON1_CLICKED)
screen.keypad( 1 )
Y,X = screen.getmaxyx()
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(2,curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3,curses.COLOR_WHITE, curses.COLOR_CYAN)
highlightText = curses.color_pair( 3 )
normalText = curses.A_NORMAL
#screen.border( 0 )
#screen.bkgd(curses.color_pair( 2 ))
curses.curs_set( 0 )
max_row = (Y)//4 #max number of rows
box1 = curses.newwin( max_row +2, (X)//3, 0, 0 )
#box1.bkgd(curses.color_pair(3))
box1.box()

strings = [ "a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "m", "n" ] #list of strings
row_num = len( strings )

pages = int( ceil( row_num / max_row ) )
position = 1
page = 1
for i in range( 1, max_row + 1 ):
    if row_num == 0:
        box1.addstr( 1, 1, "There aren't strings", highlightText )
    else:
        if (i == position):
            box1.addstr( i, 2, str( i ) + " - " + strings[ i - 1 ], highlightText )
        else:
            box1.addstr( i, 2, str( i ) + " - " + strings[ i - 1 ], normalText )
        if i == row_num:
            break

screen.refresh()
box1.refresh()

x = screen.getch()
while x != 27:
    if x == curses.KEY_DOWN:
        if page == 1:
            if position < i:
                position = position + 1
            else:
                if pages > 1:
                    page = page + 1
                    position = 1 + ( max_row * ( page - 1 ) )
        elif page == pages:
            if position < row_num:
                position = position + 1
        else:
            if position < max_row + ( max_row * ( page - 1 ) ):
                position = position + 1
            else:
                page = page + 1
                position = 1 + ( max_row * ( page - 1 ) )
    if x == curses.KEY_UP:
        if page == 1:
            if position > 1:
                position = position - 1
        else:
            if position > ( 1 + ( max_row * ( page - 1 ) ) ):
                position = position - 1
            else:
                page = page - 1
                position = max_row + ( max_row * ( page - 1 ) )
    if x == curses.KEY_LEFT:
        if page > 1:
            page = page - 1
            position = 1 + ( max_row * ( page - 1 ) )

    if x == curses.KEY_RIGHT:
        if page < pages:
            page = page + 1
            position = ( 1 + ( max_row * ( page - 1 ) ) )
    if x == ord( "\n" ) and row_num != 0:
        screen.erase()
        #screen.border( 0 )
        screen.addstr( Y-1, 3 , "YOU HAVE PRESSED '" + strings[ position - 1 ] + "' ON POSITION " + str( position ) )
    box1.erase()
    #screen.border( 0 )
    box1.border( 0 )

    for i in range( 1 + ( max_row * ( page - 1 ) ), max_row + 1 + ( max_row * ( page - 1 ) ) ):
        if row_num == 0:
            box1.addstr( 1, 1, "There aren't strings",  highlightText )
        else:
            if ( i + ( max_row * ( page - 1 ) ) == position + ( max_row * ( page - 1 ) ) ):
                box1.addstr( i - ( max_row * ( page - 1 ) ), 2, str( i ) + " - " + strings[ i - 1 ], highlightText )
            else:
                box1.addstr( i - ( max_row * ( page - 1 ) ), 2, str( i ) + " - " + strings[ i - 1 ], normalText )
            if i == row_num:
                break



    screen.refresh()
    box1.refresh()
    x = screen.getch()

curses.endwin()
