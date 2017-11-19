#!/usr/bin/python3


def move_add(moves, movenum, card1, card2):

    #print("card1 is {} and card2 is {}".format(type(card1), type(card2)))

    if movenum not in moves:
        moves[movenum] = []
    
    moves[movenum].append((card1.index, card2.index))


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



if __name__ == '__main__':


    import solitaire

    s = solitaire.Solitaire()



    noprogresscount = 0
    movesmade = {}
    movenum = 0
    
    # Endlessly loop over the available moves. Give up if we complete 3 loops
    # without any progress.
    while True:

        movenum += 1

        if noprogresscount == 3:
            print("Game seems unsolvable. Giving up after {} moves!".format(movenum))
            print(str(s))
            exit(1)

        progress = False

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


        # Check for cards that can be moved from stacks to collections.
        for pile in s.piles:
            topcard = pile.showtop()

            if topcard:
                for coll in s.collections:
                    if coll.push(topcard):
                        pile.pop()

                        print("Moved {} from a pile to a collection!".format(topcard))
                        progress = True
                        break


        # Check to see if cards can be moved between stacks
        for pile in s.piles:
            topcard = pile.showtop()
            if topcard:
                for newpile in s.piles:
                    if pile.index != newpile.index:
                        if newpile.canPush(topcard):
                            undercard = newpile.showtop()
                            newpile.push(topcard)
                            topcard2 = pile.pop()

                            # quick check to make sure my logic is sound
                            if topcard.index != topcard2.index:
                                print("CHECK STACK-TO-STACK LOGIC")
                                exit(2)


                            print("Moved {} from a stack to another stack on top of {}!".format(topcard, undercard))
                            move_add(movesmade, movenum, topcard, undercard)
                            progress = True
                            break

        # Check for cards that can be moved from the pool to collections or stacks.
        # Note: since this can lead to unwinnable situations, we only do this if there's been
        # no progress thus far in the turn.
        if not s.pool.isEmpty() and not progress:
            poolsize = s.pool.size()
            for i in range(0,poolsize):
                topcard = s.pool.advance()

                done = False

                for coll in s.collections:
                    if coll.push(topcard):
                        topcard2 = s.pool.pop()

                        # quick check to make sure my logic is sound
                        if topcard.index != topcard2.index:
                            print("CHECK POOL-TO-COLLECTION LOGIC")
                            exit(2)

                        print("Moved {} from the pool to a collection!".format(topcard))
                        done = True
                        progress = True
                        break

                if not done:
                    for pile in s.piles:
                        if pile.push(topcard):
                            topcard2 = s.pool.pop()

                            # quick check to make sure my logic is sound
                            if topcard.index != topcard2.index:
                                print("CHECK POOL-TO-STACK LOGIC")
                                exit(2)

                            print("Moved {} from the pool to a pile!".format(topcard))
                            done = True
                            progress = True
                            break
        # Check to see if the game is finished...
        collcount = 0
        for coll in s.collections:
            collcount += coll.size()
        if collcount == 52:
            print("All 52 cards are in collections - we dun it baby!")
            exit(0)
        else:
            print("Turn finished. {} cards in collections.".format(collcount))

        if is_turn_duplicate(movesmade, movenum):
            print("just had a duplicate turn")
            noprogresscount += 1

        if not progress:
            noprogresscount += 1

