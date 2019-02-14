#!/usr/bin/env python

# Anthony Vaccaro, 2019
#
# draws a neat ulam spiral pattern. uses tkinter for graphical output.

from time import sleep
import math
from tkinter import *
import itertools

# right, up, left, down
moves = itertools.cycle([(1, 0), (0, -1), (-1,  0), (0, 1)])

def calc_primes(max=5000):

    nums = {}
    
    for i in range(1,max+1):
        nums[i] = True

    for x in range(2,max):
        for y in range(2,max):
            sum = x * y
            if sum > max:
                break
            nums[sum] = False

    nums[1] = False
    return nums

def main():


    master = Tk()

    dimx = 300
    dimy = 300
   
    primes = calc_primes(dimx * dimy)

    c = Canvas(master, width=dimx, height=dimy)
    c.pack()

    grid = []

    for row in range(0,dimx):
        grid.append([0 for x in range(0,dimy)])

    x = math.ceil(dimx/2)
    y = math.ceil(dimy/2)

    thismove = next(moves)
    nextmove = next(moves)

    primecount = 0
    numcount = 0

    for n in range(1, dimx * dimy):
        #sleep(0.01)
        p = primes[n]
        numcount += 1
        x = x + thismove[0]
        y = y + thismove[1]
        try:
            if p:
                colour = 'red'
                grid[y][x] = 1
                primecount += 1
            else:
                colour = 'white'
                grid[y][x] = 2
        except IndexError:
            break

        #print("added {} which is {}-prime".format(n, p))
        c.create_line(x, y, x, y, fill=colour)
        
        # play with this to adjust speed
        if n % 100 == 0:
            master.update()
       
        nx = x + nextmove[0]
        ny = y + nextmove[1]
        
        if grid[ny][nx]:
            continue

        thismove = nextmove
        nextmove = next(moves)

    print("spiral complete! {} of the {} pixels drawn were primes.".format(primecount, numcount))
    mainloop()

if __name__ == "__main__":
    main()

