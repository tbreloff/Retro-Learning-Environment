#!/usr/bin/env python
# python_example.py
# Author: Tom Breloff
#
# Modeled on python_example.py

import sys, os
from random import randrange
from rle_python_interface import RLEInterface

romname = os.path.join(os.getenv("HOME"), "roms/super_mario_world.sfc")
corename = "snes"
if len(sys.argv) > 1:
    romname = sys.argv[1]
if len(sys.argv) > 2:
    corename = sys.argv[2]
print("romname =", romname, "corename=", corename)

rle = RLEInterface()

# Get & Set the desired settings
# rle.setInt('random_seed', 123)

# Set USE_SDL to true to display the screen. RLE must be compilied
# with SDL enabled for this to work. On OSX, pygame init is used to
# proxy-call SDL_main.
USE_SDL = True
if USE_SDL:
  if sys.platform == 'darwin':
    import pygame
    pygame.init()
    rle.setBool('sound', False) # Sound doesn't work on OSX
  elif sys.platform.startswith('linux'):
    rle.setBool('sound', True)
  rle.setBool('display_screen', True)

# Load the ROM file
rle.loadROM(romname, corename)

# Get the list of legal actions
minimal_actions = rle.getMinimalActionSet()

NOOP = 0
JUMP = 1
RUN = 2
UP = 16
DOWN = 32
LEFT = 64
RIGHT = 128
SPIN = 256

n = rle.getRAMSize()

# retrieve ram value for SMW
def getram(hexval):
    mem = rle.getRAM()
    return hex(mem[hexval-0x7E0000])

# set a value in ram for SMW
def setram(hexval, val):
    rle.setRAM(hexval-0x7E0000, val)

gamemode_offset = 0x7E0100
overworld_hack_offset = 0x7E0109

# print(getram(gamemode_offset))
# setram(gamemode_offset, 30)
# print(getram(gamemode_offset))

def load_level(level):
    rle.reset_game()

    if level:
        # do the overworld level override hack (https://www.smwcentral.net/?p=nmap&m=smwram#7E0109)
        setram(overworld_hack_offset, level)
        # trigger the overworld loading, which in turn triggers the level load
        setram(gamemode_offset, 0x0C)

        # wait for level load
        for i in range(100):
            rle.act(NOOP)

    else:
        # leave the loading world to the right
        for i in range(200):
            rle.act(RIGHT | RUN)


# Play 10 episodes
for episode in xrange(10):
    # load a random level
    level = randrange(20)+1
    print("Loading level", level)
    load_level(level)

    # run the episode
    total_reward = 0
    # lastmode = 0
    while not rle.game_over():
        a = minimal_actions[randrange(len(minimal_actions))]
        # Apply an action and get the resulting reward
        reward = rle.act(RIGHT | RUN | a)
        total_reward += reward

        # mode = getram(gamemode_offset)
        # if mode != lastmode:
        #     print("New game mode:", mode)
        #     lastmode = mode

    print 'Episode', episode, 'ended with score:', total_reward
