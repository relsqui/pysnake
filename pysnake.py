#!/usr/bin/python
# coding=UTF-8

import curses, time, random, locale


## SETTINGS ##

# What character should be used to represent each of these?
HEAD = "@"
ROCK = "#"
GEM = "*"
TROPHY = "!"

# How would you like to control the snake?
PAUSE_KEYS = [ord(' '), ord('p')]
QUIT_KEYS = [ord('q')]
LEFT_KEYS = [curses.KEY_LEFT, ord('h'), ord('a')]
RIGHT_KEYS = [curses.KEY_RIGHT, ord('l'), ord('d')]
UP_KEYS = [curses.KEY_UP, ord('k'), ord('w')]
DOWN_KEYS = [curses.KEY_DOWN, ord('j'), ord('s')]

# What are the treat characters, in order?
# Unicode is okay, but curses plays better with some characters than others.
TREATS = u"1234567890"

# This is the denominator of the probability that a gem will appear on any
# given iteration of the main loop, so lower number == higher chance.
# Set to 0 to remove random gems altogether.
GEMCHANCE = 250

# How many rocks need to appear before they all turn into gems?
# Set to 0 to prevent this from happening.
ROCKSTOGEMS = 5

# How many gems need to appear before they turn into a trophy?
# Set to 0 to prevent this from happening.
GEMSTOTROPHY = 10

# Slow vs. fast loop allows for different rates of horizontal/vertical
# movement (to make up for characters being taller than they are wide).
# Loop times are the delay per game turn, in seconds--lower is faster.
SLOWLOOP = 0.2
FASTLOOP = 0.15

# How much should the game speed up when you complete a treat set?
# Set to 1 to prevent this from happening. Values lower than 1
# will make the game slow down instead of speeding up.
SPEED_UP = 1.2

# Should the edges wrap around (as opposed to being obstacles)?
EDGEWRAP = True

## END SETTINGS ##


# Some initialization happens outside the curses wrapper, because we'll still
# need the information after it exits.

locale.setlocale(locale.LC_ALL,"")

head = (0, 0)
vector = (0, 1)
segments = []
length = startlength = len(TREATS)

treats = []
lasttreat = len(TREATS) - 1
nexttreat = 0

rocks = []
gems = []
gems_collected = 0
trophies = []
trophies_collected = 0

gameover = None
looptime = FASTLOOP
speed_factor = 1


def game(stdscr):
    global vector, length, looptime, speed_factor, lasttreat, nexttreat
    global gems_collected, trophies_collected, gameover

    # Function definitions are inside the curses wrapper so they'll have access
    # to the window object.

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

    def location_empty(loc, obstacles_only = False):
        global head
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
        if loc in rocks:
            return False
        if obstacles_only:
            # This is at least a safe location for the snake head.
            return True

        if loc in treats:
            return False
        if loc in gems:
            return False
        if loc in trophies:
            return False
        if loc == head:
            return False
        # This location is definitely really empty.
        return True

    def pick_empty():
        global head
        spot = head
        while not location_empty(spot):
            spot = (random.randrange(0, curses.LINES-1),
                    random.randrange(0, curses.COLS-1))
        return spot

    def make_treat(i):
        treat = pick_empty()
        treats[i] = treat
        safe_put(TREATS[i], treat)

    def make_rock():
        global rocks
        new_rock = pick_empty()
        rocks.append(new_rock)
        safe_put(ROCK, new_rock)
        if ROCKSTOGEMS and len(rocks) >= ROCKSTOGEMS:
            for rock in rocks:
                make_gem(rock)
            rocks = []

    def make_gem(new_gem=None):
        global gems
        if not new_gem:
            new_gem = pick_empty()
        gems.append(new_gem)
        safe_put(GEM, new_gem)
        if GEMSTOTROPHY and len(gems) >= GEMSTOTROPHY:
            for gem in gems:
                safe_put(" ", gem)
            gems = []
            make_trophy()

    def make_trophy():
        new_trophy = pick_empty()
        trophies.append(new_trophy)
        safe_put(TROPHY, new_trophy)


    for i in range(len(TREATS)):
        # We don't use make_treat() to initialize this because it will try to
        # replace the previous value, which doesn't exist yet.
        new_treat = pick_empty()
        treats.append(new_treat)
        safe_put(TREATS[i], new_treat)

    head = (int(curses.LINES/2), int(curses.COLS/2))
    safe_put(HEAD, head)
    stdscr.move(head[0], head[1])
    stdscr.nodelay(1)

    while True:
        c = stdscr.getch()
        if c in PAUSE_KEYS:
            stdscr.nodelay(0)
            c = None
            while c not in PAUSE_KEYS + QUIT_KEYS:
                c = stdscr.getch()
            stdscr.nodelay(1)
        elif c in LEFT_KEYS:
            vector = (0, -1)
            looptime = FASTLOOP
        elif c in RIGHT_KEYS:
            vector = (0, 1)
            looptime = FASTLOOP
        elif c in UP_KEYS:
            vector = (-1, 0)
            looptime = SLOWLOOP
        elif c in DOWN_KEYS:
            vector = (1, 0)
            looptime = SLOWLOOP

        if c in QUIT_KEYS:
            # This is separate so it'll be executed after a pause command.
            gameover = "Player quit."
            break

        if head in treats:
            i = treats.index(head)
            if TREATS[i] != TREATS[nexttreat]:
                gameover = ("Collected treat out of order.")
                break
            length += 1
            make_treat(i)
            lasttreat = nexttreat
            nexttreat = (nexttreat + 1) % len(TREATS)
            if nexttreat == 0:
                make_rock()
                speed_factor = speed_factor * SPEED_UP
        elif head in gems:
            gems.remove(head)
            gems_collected += 1
        elif head in trophies:
            trophies.remove(head)
            trophies_collected += 1
        elif not location_empty(head, True):
            gameover = "Bumped into something."
            break

        if GEMCHANCE and not random.randint(0, GEMCHANCE-1):
            make_gem()

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

        if length:
            segments.insert(0, head)
            if len(segments) > length:
                safe_put(" ", segments.pop())
            draw_segments()
        else:
            safe_put(" ", head)

        head = newhead
        safe_put(HEAD, head)
        stdscr.move(head[0], head[1])
        stdscr.refresh()
        time.sleep(looptime / speed_factor)

def s(number):
    if number == 1:
        return ""
    return "s"

def ies(number):
    if number == 1:
        return "y"
    return "ies"

curses.wrapper(game)
print("{message} You win!\nYou collected {treats} treat{ts}, {gems} gem{gs}, "
      "and {trophies} troph{ies}.".format(message=gameover,
                                          treats=length-startlength,
                                          ts=s(length-startlength),
                                          gems=gems_collected,
                                          gs=s(gems_collected),
                                          trophies=trophies_collected,
                                          ies=ies(trophies_collected)))
