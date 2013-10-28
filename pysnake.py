#!/usr/bin/python
# coding=UTF-8


## SETTINGS ##

# What character should be used to represent each of these?
HEAD = "@"
ROCK = "#"
GEM = "*"

# What are the unique treat characters, in order?
# Unicode is okay, but curses plays better with some alphabets than others.
TREATS = u"0123456789"

# This is the denominator of the probability that a gem will appear on any
# given iteration of the main loop, so lower number == higher chance.
# Set to 0 to remove random gems altogether.
GEMCHANCE = 250

# How many rocks need to appear before they all turn into gems?
# Set to 0 to prevent this from happening.
ROCKSTOGEMS = 5

# How long is the snake at the beginning?
STARTLENGTH = len(TREATS)

# Slow vs. fast loop allows for different rates of horizontal/vertical
# movement (to make up for characters being taller than they are wide).
# Loop times are the delay per game turn, in seconds--lower is faster.
SLOWLOOP = 0.2
FASTLOOP = 0.15

# Should the edges wrap around (as opposed to being obstacles)?
EDGEWRAP = True

## END SETTINGS ##


import curses, time, random, locale
locale.setlocale(locale.LC_ALL,"")

head = (0, 0)
vector = (0, 1)
segments = []
length = STARTLENGTH

treats = []
lasttreat = len(TREATS) - 1
nexttreat = 0

rocks = []
gems = []
gems_collected = 0

gameover = None
looptime = FASTLOOP


def game(stdscr):
    # Function definitions are inside the curses wrapper so they'll have access
    # to the window object, which they all need.

    def safe_put(char, loc):
        # This is a workaround; curses won't print to the bottom right spot.
        if loc[0] == curses.LINES-1 and loc[1] == curses.COLS-1:
            stdscr.addstr(loc[0], loc[1]-1, char.encode("utf-8"))
            stdscr.insstr(loc[0], loc[1]-1, " ")
        else:
            stdscr.addstr(loc[0], loc[1], char.encode("utf-8"))

    def draw_segments():
        for i in range(len(segments)):
            segment_string = TREATS[(lasttreat - i) % len(TREATS)]
            safe_put(segment_string, segments[i])

    def location_empty(loc):
        if not EDGEWRAP:
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
        if loc in treats:
            return False
        if loc in rocks:
            return False
        if loc in gems:
            return False
        if loc == head:
            return False
        return True

    def pick_empty():
        spot = head
        while not location_empty(spot):
            spot = (random.randrange(0, curses.LINES-1),
                    random.randrange(0, curses.COLS-1))
        return spot

    def make_treat(i):
        treat = pick_empty()
        try:
            treats[i] = treat
        except IndexError:
            # This happens when treats is being initialized.
            treats.append(treat)
        safe_put(TREATS[i], treat)

    def make_rock():
        global rocks
        rock = pick_empty()
        rocks.append(rock)
        safe_put(ROCK, rock)
        if ROCKSTOGEMS and len(rocks) >= ROCKSTOGEMS:
            for rock in rocks:
                make_gem(rock)
            rocks = []

    def make_gem(loc=None):
        if not loc:
            loc = pick_empty()
        gems.append(loc)
        safe_put(GEM, loc)

    stdscr.nodelay(1)
    head = (int(curses.LINES/2), int(curses.COLS/2))
    safe_put(HEAD, head)
    stdscr.move(head[0], head[1])

    for i in range(len(TREATS)):
        make_treat(i)

    global vector, length, looptime, lasttreat, nexttreat, gems_collected, gameover
    while True:
        if GEMCHANCE and not random.randint(0, GEMCHANCE-1):
            make_gem()

        c = stdscr.getch()
        if c in [ord(' '), ord('p')]:
            stdscr.nodelay(0)
            c = None
            while c not in [ord(' '), ord('p'), ord('q')]:
                c = stdscr.getch()
            stdscr.nodelay(1)
        elif c in [curses.KEY_LEFT, ord('h'), ord('a')]:
            vector = (0, -1)
            looptime = FASTLOOP
        elif c in [curses.KEY_RIGHT, ord('l'), ord('d')]:
            vector = (0, 1)
            looptime = FASTLOOP
        elif c in [curses.KEY_UP, ord('k'), ord('w')]:
            vector = (-1, 0)
            looptime = SLOWLOOP
        elif c in [curses.KEY_DOWN, ord('j'), ord('s')]:
            vector = (1, 0)
            looptime = SLOWLOOP

        if c == ord('q'):
            # This is separate so it'll be executed after a pause command.
            gameover = "Player quit."
            break

        new_y = head[0] + vector[0]
        new_x = head[1] + vector[1]
        if EDGEWRAP:
            if new_y < 0:
                new_y = curses.LINES - 1
            elif new_y >= curses.LINES:
                new_y = 0
            if new_x < 0:
                new_x = curses.COLS - 1
            elif new_x >= curses.COLS:
                new_x = 0
        newhead = (new_y, new_x)

        if (not location_empty(newhead)
            and newhead not in treats and newhead not in gems):
            gameover = "Bumped into something."
            break

        if length:
            segments.insert(0, head)
            safe_put(str(lasttreat), head)
            if len(segments) > length:
                safe_put(" ", segments.pop())
            draw_segments()
        else:
            safe_put(" ", head)
        head = newhead
        safe_put(HEAD, head)

        if head in treats:
            i = treats.index(head)
            if i != nexttreat:
                gameover = ("Collected treat out of order.")
                break
            length += 1
            make_treat(i)
            lasttreat = nexttreat
            nexttreat = (i + 1) % len(TREATS)
            if nexttreat == 0:
                make_rock()

        if head in gems:
            gems.remove(head)
            gems_collected += 1

        stdscr.move(head[0], head[1])
        stdscr.refresh()
        time.sleep(looptime)

def s(number):
    if number == 1:
        return ""
    return "s"

curses.wrapper(game)
print("{message} You win! You collected {treats} treat{ts} and {gems} "
      "gem{gs}.".format(message=gameover,
                        treats=length-STARTLENGTH, ts=s(length-STARTLENGTH),
                        gems=gems_collected, gs=s(gems_collected)))
