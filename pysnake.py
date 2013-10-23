#!/usr/bin/python

import curses
import time
import random


HEAD = "@"
SEGMENT = "0"
TREAT = "!"

head = (0, 0)
vector = (0, 0)
segments = []
length = 3

speed = .15
lastmoved = 0

treats = []
treatcount = 1

def game(stdscr):
    def location_ok(loc):
        if loc[0] < 0:
            return False
        if loc[0] > curses.LINES-1:
            return False
        if loc[1] < 0:
            return False
        if loc[1] > curses.COLS-1:
            return False
        if loc in segments:
            return False
        return True

    def safe_put(char, loc):
        # this is a workaround because curses won't print
        # to the bottom right spot in a window
        if loc[0] == curses.LINES-1 and loc[1] == curses.COLS-1:
            stdscr.addstr(loc[0], loc[1]-1, char)
            stdscr.insstr(loc[0], loc[1]-1, " ")
        else:
            stdscr.addstr(loc[0], loc[1], char)

    def make_treat():
        treat = head
        while treat == head or treat in treats or treat in segments:
            treat = (random.randrange(0, curses.LINES-1),
                     random.randrange(0, curses.COLS-1))
        safe_put(TREAT, treat)
        return treat

    stdscr.nodelay(1)
    head = (int(curses.LINES/2), int(curses.COLS/2))
    treats.append(make_treat())
    safe_put(HEAD, head)
    stdscr.move(head[0], head[1])

    global vector, length, lastmoved
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            break
        elif c in [curses.KEY_LEFT, ord('h'), ord('a')]:
            vector = (0, -1)
        elif c in [curses.KEY_RIGHT, ord('l'), ord('d')]:
            vector = (0, 1)
        elif c in [curses.KEY_UP, ord('k'), ord('w')]:
            vector = (-1, 0)
        elif c in [curses.KEY_DOWN, ord('j'), ord('s')]:
            vector = (1, 0)

        if vector != (0, 0) and lastmoved + speed < time.clock():
            lastmoved = time.clock()
            newhead = (head[0] + vector[0], head[1] + vector[1])
            if location_ok(newhead):
                if len(segments) >= length:
                    tail = segments.pop()
                    safe_put(" ", tail)
                segments.insert(0, head)
                safe_put(SEGMENT, head)
                head = newhead
                safe_put(HEAD, head)
                if head in treats:
                    length += 1
                    treats.remove(head)
                if len(treats) < treatcount:
                    treats.append(make_treat())
                stdscr.move(head[0], head[1])
            else:
                break

        stdscr.refresh()

curses.wrapper(game)
print("You win! Final snake length: {}.".format(length))
