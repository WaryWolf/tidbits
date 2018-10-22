#!/usr/bin/python3

from timeit import default_timer as timer

import solitaire

import argparse


# this function checks to make sure that cards aren't just being swapped
# back and forth between piles.
def is_pile_thrashing(moves):

    # not enough moves to be thrashing yet
    if len(moves) <= 2:
        return False

    if None in moves[-3:]:
        return is_pile_thrashing_2(moves)

    move1 = moves[-1]
    move2 = moves[-2]
    move3 = moves[-3]

    if move1[0] == 'PiPi' and move2[0] == 'PiPi' and move3[0] == 'PiPi':
        #if (move1[1][0] == move3[1][0]) and (move1[1][1] == move3[1][1]):
        if (move1[1][1] == move3[1][1]):
            return True

    #print("nah")
    return False

def is_pile_thrashing_2(moves):

    #print(moves)

    move1 = moves[-1]
    move2 = moves[-2]
    move3 = moves[-3]

    #if move1 == None or move3 == None:
    #    return False

    if move1 and move2:
        if move1[0] == 'PiPi' and move2[0] == 'PiPi':
            if move1[1][1] == move2[1][1]:
                return True

    if move1 and move3:
        if move1[0] == 'PiPi' and move2 == None and move3[0] == 'PiPi':
            #print(moves)
            #exit(1)
            if (move1[1][1] == move3[1][1]):
                #print("is3")
                return True

    if move2 and move3:
        if move2[0] == 'PiPi' and move3[0] == 'PiPi':
            if move2[1][1] == move3[1][1]:
                return True

    if move3 and (not move1 and not move2):
        if len(moves) > 3:
            move4 = moves[-4]
            if move4 and move4[0] == 'PiPi':
                #print("yes4")
                if move4[1][1] == move3[1][1]:
                    #print("is4")
                    return True

    elif move2 and (not move1 and not move3):
        #print("yes3: {} {} {}".format(move1, move2, move3))
        if len(moves) > 3:
            move4 = moves[-4]
            if move4 and move4[0] == 'PiPi':
                #print("yes4")
                if move4[1][1] == move2[1][1]:
                    #print("is4")
                    return True
                if move1[1][1] == move4[1][1]:
                    #print("is5")
                    return True

    #print("nah2: {}".format(moves[-4:]))
    return False

def move_pile_collection(solitaire, reveal_only=False):

    for pile in solitaire.piles:
        topcard = pile.showTop()

        if topcard:
            for coll in solitaire.collections:
                if coll.can_push(topcard):
                    undercard = coll.showtop()
                    coll.push(topcard)
                    topcard2 = pile.pop()
                    
                    #XXX remove for speed
                    if topcard.index != topcard2.index:
                        print("CHECK PILE-TO-COLLECTION LOGIC")
                        exit(2)

                    #print("Moved {} from a pile to a collection!".format(topcard))
                    #return topcard
                    return ("PiC",(undercard, topcard))
    return False


def move_pool_collection(solitaire):
    poolsize = solitaire.pool.size()
    for i in range(0,poolsize):
        topcard = solitaire.pool.advance()
        
        for coll in s.collections:
            if coll.can_push(topcard):
                undercard = coll.showtop()
                coll.push(topcard)
                topcard2 = s.pool.pop()

                # XXX remove for speed
                if topcard.index != topcard2.index:
                    print("CHECK POOL-TO-COLLECTION LOGIC")
                    exit(2)

                #print("Moved {} from the pool to a collection!".format(topcard))
                #return topcard
                return ("PoC",(undercard, topcard))

    return False

def move_pool_piles(solitaire):
    poolsize = s.pool.size()
    for i in range(0,poolsize):
        topcard = s.pool.advance()
        for pile in solitaire.piles:
            if pile.canPush(topcard):
                undercard = pile.showTop()
                pile.push(topcard)
                
                
                # XXX remove for speed
                topcard2 = solitaire.pool.pop()
                # quick check to make sure my logic is sound
                if topcard.index != topcard2.index:
                    print("CHECK POOL-TO-STACK LOGIC")
                    exit(2)

                #print("Moved {} from the pool to a pile on top of {}!".format(topcard, undercard))
                #return topcard
                return ("PoPi", (undercard, topcard))

    return False

# Check to see if cards can be moved between piles. If a move is found,
# perform the move and return the cards moved.

# for multiple-card moves, we need to keep track of:
#  - which card matches the new pile
#  - how many cards to pop off the old pile
#  - how many cards to push to the new pile (should be same as above)
def move_between_piles(solitaire, reveal_only=False): 
    for pile in solitaire.piles:
        #topcard = pile.showTop()
        topcards = pile.showAll()
        if topcards:
            for index, card in enumerate(topcards):

                if reveal_only and index != 0: # skip ahead if we're only interested in revealing more hidden cards
                    break

                for newpile in solitaire.piles:
                    if pile.index != newpile.index: # stop bad things from happening
                        if newpile.canPush(card):


                            # very dirty check to stop kings getting shuffled around
                            #if newpile.size() == 0 and pile.size() == 1:
                            if newpile.size() == 0 and card.rank == 13:
                                continue

                            #print("going to move {} onto a pile which has {} right now".format(topcards, newpile))

                            # work out how many cards we are going to move
                            cardnum = len(topcards) - index
                            """
                            oldpilesize = pile.size()
                            newpilesize = newpile.visSize() + cardnum
    
                            if oldpilesize >= newpilesize:
                                #print("I was about to take {} cards from a {} card pile to make a {} card pile.".format(cardnum, oldpilesize, newpilesize))
                                continue
                            """
                            
                            mcards = pile.popMany(cardnum)

                            # quick check, can remove later
                            if card.index != mcards[0].index:
                                print("CHECK STACK-TO-STACK LOGIC")
                                #print("topcards = {}".format(str(topcards)))
                                #print("newpile = {}".format(str(newpile)))
                                #print("mcards = {}".format(mcards))
                                #print("card = {}".format(card))
                                #print(str(solitaire))
                                exit(2)
                            
                            undercard = newpile.showTop()

                            newpile.pushMany(mcards)
                            
                            mcardstr = " ".join([str(x) for x in mcards])

                            if undercard:
                                #print("Moved {} from a pile to another pile on top of {}!".format(mcardstr, undercard))
                                #return (mcards, undercard)
                                return ("PiPi", (undercard, mcardstr))
                            else:
                                #print("Moved {} from a pile to an empty pile!".format(mcardstr))
                                #return (mcards,)
                                return ("PiPi", (None, mcardstr))

    """
            for newpile in solitaire.piles:
                if pile.index != newpile.index: # stop bad things from happening
                    if newpile.canPush(topcard):

                        # very dirty check to stop kings getting shuffled around
                        if newpile.size() == 0 and pile.size() == 1:
                            continue

                        undercard = newpile.showTop()

                        newpile.push(topcard)
                        topcard2 = pile.pop()
                        
                        # quick check to make sure my logic is sound
                        if topcard.index != topcard2.index:
                            print("CHECK STACK-TO-STACK LOGIC")
                            exit(2)

                        if undercard:
                            #print("Moved {} from a pile to an empty pile!".format(topcard, undercard))
                            return (topcard,)
                        else:
                            #print("Moved {} from a pile to another pile on top of {}!".format(topcard, undercard))
                            return (topcard, undercard)
    """
    return False


# searches for aces and twos and moves them to collections if possible.
def move_find_aces_twos(solitaire):

    # quick check in case all the aces/twos have been found
    donecount = 0
    for coll in solitaire.collections:
        if coll.size() > 2:
            donecount += 1
    if donecount == 4:
        return False

    poolsize = solitaire.pool.size()
    for i in range(0,poolsize):
        topcard = solitaire.pool.advance()
        
        if topcard.rank <= 2:
            for coll in s.collections:
                if coll.can_push(topcard):
                    undercard = coll.showtop()
                    coll.push(topcard)
                    topcard2 = s.pool.pop()

                    # XXX remove for speed
                    if topcard.index != topcard2.index:
                        print("CHECK POOL-TO-COLLECTION LOGIC")
                        exit(2)

                    #print("Moved {} from the pool to a collection!".format(topcard))
                    #return topcard
                    return ("PoC",(undercard, topcard))


    for pile in solitaire.piles:
        topcard = pile.showTop()
        
        if topcard and topcard.rank <= 2:
            for coll in s.collections:
                if coll.can_push(topcard):
                    undercard = coll.showtop()
                    coll.push(topcard)
                    topcard2 = pile.pop()
                    
                    # XXX remove for speed
                    if topcard.index != topcard2.index:
                        print("CHECK PILE-TO-COLLECTION LOGIC")
                        exit(2)

                    #print("Moved {} from the pool to a collection!".format(topcard))
                    #return topcard
                    return ("PiC",(undercard, topcard))



    return False

    

    

# attempts to solve a single game of solitaire using brute-force "can i do this move?" tactics.
def solve_game(s):
    
    moves = []
    last_pipi = ""

    movenum = 0
    maxmove = 500
    # loop over the available moves. Give up if we complete 3 loops
    # without any progress.
    #for movenum in range(1,maxmove):
    while movenum <= maxmove:

        movenum += 1

        # if the last 3 turns have resulted in no progress
        if moves[-3:] == [None, None, None]:
            #print("no progress, giving up")
            break

        # invariant check to make sure something hasn't gone horribly wrong
        # comment out for a decent speedup
        if not s.invariant_check():    
            print("ERROR: Invariant check failed!")
            exit(1)
       
        """
        RULE PRIORITY:

        "special" moves:
        - aces & 2s to collections (no need to be in piles)
        - kings to empty piles (consider colour of existing stacks first?)


        "good" moves:
        1. pile -> pile, revealing cards (this should be your "default" choice IMO)
        2. pile -> collection, revealing cards
        3. pool -> pile

        "low priority" moves:
        4. pool -> collection
        5. pile -> collection (only necessary at end of the game)
        
        ?? pile -> pile, not revealing cards (only useful when one collection is advanced more than another...)
        """


        # special moves
        move = move_find_aces_twos(s)
        if move:
            moves.append(move)
            continue



        # Check to see if cards can be moved between piles to reveal new cards
        move = move_between_piles(s, True)
        if move:
            moves.append(move)
            continue

        move = move_pile_collection(s)
        if move:
            moves.append(move)
            continue


        # try moving between piles, but this time allow any number of cards to be shuffled around
        if not is_pile_thrashing(moves):
            move = move_between_piles(s, False)

        if move:
            moves.append(move)
            continue

        # Check for cards that can be moved from the pool to collections or stacks.
        # Note: since this can lead to unwinnable situations, we only do this if there's been
        # no progress thus far in the turn.
        move = move_pool_piles(s)
        
        if move:
            moves.append(move)
            continue

        move = move_pool_collection(s)
        if move:
            moves.append(move)
            continue

        # Check to see if the game is finished...
        collcount = 0
        for coll in s.collections:
            collcount += coll.size()
        if collcount == 52:
            #print("All 52 cards are in collections - we dun it baby!")
            #print(str(s))
            return (True, 52, movenum)
        else:
            pass
            #print("Turn finished. {} cards in collections.".format(collcount))

        moves.append(None)
    
    # Game is unsolvable 
    #print(str(s))
    #print(moves[-10:])
    collcount = 0
    for col in s.collections:
        collcount += col.size()
    #print("Game seems unsolvable. Giving up after {} moves and {} cards in collections!".format(movenum, collcount))
    return (False, collcount, movenum)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, help="Number of games to run")
    args = parser.parse_args()
    count = args.count


    s = solitaire.Solitaire()

    res = []

    start = timer()
    for i in range(0,count):
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
