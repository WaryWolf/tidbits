# solitaire


Somewhere on the internet I read that ~77% of (klondike) solitaire games are solvable. I wanted to see how true this was, and also write a program that could solve this many solitaire games.

So far I have implemented the following:

`solitaire.py` is a representation of a solitaire game, with some basic logic to handle legal/nonlegal moves etc. I occasionally add extra methods to the API, and the implementation could be optimised for speed (particularly the `canPush()` methods, but it's basically complete.

`solitaire-client.py` is a simple client that handles benchmarking the different solvers.

`bruteforce.py` is a simple brute-force solver that just loops through the various types of moves possible in a game of solitaire, and sees if there are any legal moves that can be made. It has a very rough priority system for the types of moves that should be made, and some logic to detect endless loops, but it's overall a very basic way to solve solitaire games. This solver currently has a ~4% solve rate, which is not great, but it can attempt ~150 games a second per core on an Intel i5-2500k, so at least it's fast.

## USAGE:

```
usage: solitaire-client.py [-h] [-s {bruteforce}] [-d | -p PARALLEL] count

positional arguments:
  count                 Number of games to run

optional arguments:
  -h, --help            show this help message and exit
  -s {bruteforce}, --solver {bruteforce}
                        which solver module to use
  -d, --deterministic   produce deterministic results
  -p PARALLEL, --parallel PARALLEL
                        number of parallel processes to use
```


## Features implemented so far

* Implement complete solitaire representation
* Implement a simple solver that can solve games
* Add invariant and game-solved checks to Solitaire class
* Refactor bruteforce solver into its own file and set up work for different solvers to be implemented/benchmarked
* Add deterministic mode to RNG, so changes can be benchmarked fairly and accurately
* Add parallelism with the multiprocessing library

## TODO:

#### Next:

* add a log of moves made to the Solitaire class

#### Later:

* Optimise Solitaire class for speed
* New solver implementation using scored move weightings and a proposal system (check all possible moves before committing)
* Implement a save-rollback system on each move where multiple choices are available, and recursively try every possible combination in order to maximise solve rate
* Reproduction functionality - add a Solitaire constructor that allows you to choose the layout of the cards 

#### Never:

* Machine Learning/reinforcement-based solver! :D

## NOTES

* I use non-standard names for solitaire terms, since I started implementing this on a plane trip where I had no internet access, and the names have stuck. There's a reference in `solitaire.py`.
* I haven't implemented any kind of limits, like "vegas rules" as I think it was called in windows XP.
