#!/usr/bin/python3

from timeit import default_timer as timer

import solitaire

import argparse

# XXX UNUSED
# adds a move to the list of moves made in a turn.
def move_add(moves, movenum, card1, card2):

    #print("card1 is {} and card2 is {}".format(type(card1), type(card2)))

    if movenum not in moves:
        moves[movenum] = []

    if card1 == False:
        card1 = solitaire.Card(53)

    if card2 == False:
        card2 = solitaire.Card(53)


    moves[movenum].append((card1.index, card2.index))


# this function checks to make sure that cards aren't just being swapped
# back and forth between piles.
def is_pile_thrashing(moves, movenum):

    # not enough moves to be thrashing yet
    if len(moves) <= 2:
        return False

    if None in moves[-3:]:
        return False

    move1 = moves[-1]
    move2 = moves[-2]
    move3 = moves[-3]

    if move1[0] == 'PiPi' and move2[0] == 'PiPi' and move3[0] == 'PiPi':
        if (move1[1][0] == move3[1][0]) and (move1[1][1] == move3[1][1]):
            return True


    """
    for index in range(2,5):
        try: 
            prevmove = moves[movenum - index]
        except KeyError:
            break

        if (lastmove[0] == "PiPi") and (prevmove[0] == "PiPi"):
            if (lastmove[1][0] == prevmove[1][1]) and (lastmove[1][1] == prevmove[1][0]):
                print("pile thrashing detected: {} == {}".format(prevmov, prev2mov))
                return True
    """
    return False


def is_turn_duplicate(moves, movenum):

    try:
        last_moves = moves[movenum - 1]
        these_moves= moves[movenum]
    except KeyError:
        return False


    diff_moves = False

    for move in these_moves:
        if diff_moves == True:
            break
        for lmove in last_moves:
            if ((move[0] != lmove[0]) and (move[1] != lmove[1])) and ((move[1] != lmove[0]) and (move[0] != lmove[1])):
                diff_moves = True

    return not diff_moves

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

def solve_game(s):
    
    moves = []

    # loop over the available moves. Give up if we complete 3 loops
    # without any progress.
    for movenum in range(1,300):

        #movenum += 1

        # if the last 3 turns have resulted in no progress
        if moves[-3:] == [None, None, None]:
            break

        # invariant check: There should be 52 playing cards in the game at the start of each turn.
        count = 0
        for pile in s.piles:
            count += pile.size()
        for coll in s.collections:
            count += coll.size()
        count += s.pool.size()
        if count != 52:
            print("ERROR: {} cards in play! exiting!".format(count))
            exit(1)
       
        """
        RULE PRIORITY:

        "good" moves:
        1. pile -> pile, revealing cards (this should be your "default" choice IMO)
        2. pile -> collection, revealing cards
        3. pool -> pile

        "low priority" moves:
        4. pool -> collection
        5. pile -> collection (only necessary at end of the game)
        
        ?? pile -> pile, not revealing cards (only useful when one collection is advanced more than another...)
        """


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
        if not is_pile_thrashing(moves, movenum):
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
            return (True, 52)
        else:
            pass
            #print("Turn finished. {} cards in collections.".format(collcount))

        moves.append(None)
    

    # Game is unsolvable 
    #print(str(s))
    collcount = 0
    for col in s.collections:
        collcount += col.size()
    #print("Game seems unsolvable. Giving up after {} moves and {} cards in collections!".format(movenum, collcount))
    return (False, collcount)


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
    for game in res:
        if game[0]:
            solvecount += 1
        
        colltotal += game[1]
        if game[1] > collbest:
            collbest = game[1]

    collavg = colltotal / float(count)

    print("of {} games, {} were solved successfully. Average of {} cards were moved to collections per game.".format(len(res), solvecount, collavg))
    if solvecount == 0:
        print("Best game had {} cards moved to collections.".format(collbest))
    print("Total time taken: {0:.3f} seconds. Average game duration: {1:.4f} seconds.".format(totaldur, avgdur))
    exit(0)
