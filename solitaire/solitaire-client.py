#!/usr/bin/python3

from timeit import default_timer as timer
from multiprocessing import Pool
import argparse


import solitaire


def seed_and_solve(f, seed):

    if seed:
        s = solitaire.Solitaire(seed=seed)
    else:
        s = solitaire.Solitaire()
    return f(s)


if __name__ == '__main__':

    solvers = ['bruteforce']

    parser = argparse.ArgumentParser()

    parser.add_argument("count", type=int, help="Number of games to run")
    parser.add_argument("-s", "--solver", help="which solver module to use", type=str, choices=solvers)
    parser.add_argument("-d", "--deterministic", help="produce deterministic results", action="store_true", default=False)
    parser.add_argument("-p", "--parallel", type=int, help="number of parallel processes to use", action="store", default=1)
    args = parser.parse_args()
    count = args.count

    if args.deterministic:
        seed = "SoLiTaIrE"
    else:
        seed = None

    res = []

    if args.solver == 'bruteforce':
        import bruteforce
        solve_game = bruteforce.bruteforce_solve_game
    else:
        print("Error: invalid solver chosen")
        exit(1)

    start = timer()
    if args.parallel > 1:
        jobs = []
        with Pool(args.parallel) as p:
            for i in range(0, count):
                if seed:
                    tseed = seed + str(i)
                jobs.append(p.apply_async(seed_and_solve, (solve_game, tseed)))
            p.close()
            p.join()
            for job in jobs:
                res.append(job.get(timeout=1))
    else:
        for i in range(0,count):

            if seed:
                s = solitaire.Solitaire(seed=seed + str(i))
            else:
                s = solitaire.Solitaire()

            res.append(solve_game(s))

    end = timer()

    totaldur = end - start
    avgdur = totaldur / float(count)

    solvecount = 0
    colltotal = 0
    collbest = 0
    turntotal = 0
    turnbest = 99999
    for game in res:
        if game[0]:
            solvecount += 1
        
        colltotal += game[1]
        turntotal += game[2]
        if game[1] > collbest:
            collbest = game[1]
        if game[2] < turnbest:
            turnbest = game[2]

    turnavg = turntotal / float(count)
    collavg = colltotal / float(count)

    print("of {} games, {} were solved successfully. Average of {} turns taken per game. Average of {} cards were moved to collections per game.".format(len(res), solvecount, turnavg, collavg))
    if solvecount == 0:
        print("Best game had {} cards moved to collections.".format(collbest))
    print("Total time taken: {0:.3f} seconds. Average game duration: {1:.4f} seconds.".format(totaldur, avgdur))
    exit(0)
