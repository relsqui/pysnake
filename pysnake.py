#!/usr/bin/python

import curses, time, random


HEAD = "@"
SEGMENT = "0"
TREAT = "!"

head = (0, 0)
vector = (0, -1)
segments = []
length = 3

# Loop times are in seconds.
# Slow vs. fast loop allows for different rates of horizontal/vertical
# movement (to make up for characters being taller than they are wide).
slowloop = 0.2
fastloop = 0.15
looptime = fastloop

treats = []
treatcount = 10


def game(stdscr):
    # Function definitions are inside the curses wrapper
    # so they'll have access to window context etc.
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
        # This is a workaround; curses won't print to the bottom right spot.
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

    global vector, length, looptime
    while True:
        c = stdscr.getch()
        if c == ord(' '):
            stdscr.nodelay(0)
            c = None
            while c not in [ord(' '), ord('q')]:
                c = stdscr.getch()
            stdscr.nodelay(1)
        elif c in [curses.KEY_LEFT, ord('h'), ord('a')]:
            vector = (0, -1)
            looptime = fastloop
        elif c in [curses.KEY_RIGHT, ord('l'), ord('d')]:
            vector = (0, 1)
            looptime = fastloop
        elif c in [curses.KEY_UP, ord('k'), ord('w')]:
            vector = (-1, 0)
            looptime = slowloop
        elif c in [curses.KEY_DOWN, ord('j'), ord('s')]:
            vector = (1, 0)
            looptime = slowloop

        if c == ord('q'):
            # This is separate so it'll be executed even after a pause command.
            break

        newhead = (head[0] + vector[0], head[1] + vector[1])
        if not location_ok(newhead):
            break

        if len(segments) >= length:
            safe_put(" ", segments.pop())
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
        stdscr.refresh()
        time.sleep(looptime)

curses.wrapper(game)
print("You win! Final snake length: {0}.".format(length))
