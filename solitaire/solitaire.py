#!/usr/bin/python3


# I am drunk and on a plane and I felt like writing a solitaire solver in python. 
# Too bad it'll take me a lot longer than the duration of this flight to finish it,
# but maybe i can finish it this time...

# GLOSSARY OF TERMS:

# TODO: rename Pool to Stock/Waste, Collection to Foundation, Stack to Tableau.

# "Deck" = the set of 52 cards that make up all of the cards in the game.
# "Pile" = the seven arrangements of cards at the bottom of the screen. At the start of the game only one card is visible on each pile.
# "Stack" = the part of the pile that is face up. Must have alternating colours and descending ranks for each card.
# "Collection" = the four slots at the top of the screen where cards can be stored. The objective of the game is to store 
# "Pool" = the bunch of "spare" cards at the top right of the screen (sometimes top left...) that player shuffle through in order to progress the game. 

# GAME RULES:

# At the start of the game there should be 28 cards in the seven piles. 21 of these should be face-down.
# There should be (52 - 28) 24? cards in the pool.

# The objective of the game is to get all 52 cards in the deck into the 4 collections. In order to do this, players can make the following valid moves:
#
# * placing eligible cards into collections directly (aces first).
# * placing eligible cards in piles on top of one another to create stacks, which can also reveal face-down cards in the piles. 
# * placing eligible cards from the pool onto the piles to create stacks, or directly into collections.
# * shuffling through the pool to find more eligible cards.
# * ... ? more?


import os
import sys
import random
import logging

DEFAULT_LOGGING_FORMAT = '[%(levelname)s] %(message)s'

#log = logging.Logger("solitaire", level=logging.DEBUG)
log = logging.Logger("solitaire", level=logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
handler.setFormatter(formatter)
log.addHandler(handler)


# I haven't written a python class in like 7 years

class Collection(object):

    def __init__(self, index):
        self.coll = []
        self.suit = None
        self.index = index

    def __repr__(self):
        return self.coll.__repr__()

    def __str__(self):
        #return self.coll.__str__()
        rstr = ""
        for c in self.coll:
            rstr += "{} ".format(c)
        return rstr

    # Try to push a card onto the collection. 
    # Return True if successful.
    # Return False if card is not valid for pushing.
    def push(self, card):
        if self.can_push(card):
            self._do_push(card)
            return True
        else:
            return False

    def can_push(self, card):
        if len(self.coll) == 0:

            # only an Ace can start a collection.
            if card.rank == 1:
                return True
            else:
                return False

        else:

            # Early exit due to suit mismatch. Stay fashion conscious!
            if card.suit != self.suit:
                return False

            topcard = self.coll[-1]

            if card.suit == topcard.suit:
                if card.rank == (topcard.rank + 1):
                    return True

            return False

    def _do_push(self, card):
        if len(self.coll) == 0:
            self.suit = card.suit
        
        self.coll.append(card)

    

    # Try to pop out a card from the collection.
    # Return the card if successful
    # Return False if not successful
    def pop(self):
        if len(self.coll) == 0:
            return False

        else:
            return self.coll.pop()


    # Return the top card in the collection.
    # Return false if collection is empty.
    def showtop(self):
        if len(self.coll) == 0:
            return False
        else:
            topcard = self.coll[-1]
            return topcard

    # Return all cards in the collection.
    def showall(self):
        return self.coll

    # Return size (length) of the collection.
    def size(self):
        return len(self.coll)


    # Return "Full-ness" of the collection.
    # A collection is "Full" if it has all 13 cards in the deck in it.
    def isFull(self):
        if len(self.coll) == 13:
            return True
        else:
            return False

    def isEmpty(self):
        if len(self.coll) == 0:
            return True
        else:
            return False


# thin layer on top of an array, try to treat it like a ring buffer or something?
# only need to remove and show cards after initialisation, no need for insert operation.
# There should only be 24 cards in the pool at any one time.
# TODO add "draw-three" support (longterm)
class Pool(object):

    def __init__(self, poolcards):

        self.pool = []
        self.index = 0

        #if len(poolcards) > 24:
        #    except Exception("pool's full!")

        for card in poolcards:
            self.pool.append(card)

        # shuffle the pool after populating, just in case.
        random.shuffle(self.pool)
        log.debug("created Pool instance with {} cards".format(len(self.pool)))

    def __repr__(self):
        return self.pool.__repr__()

    def __str__(self):
        rstr = ""
        for c in self.pool:
            rstr += "{} ".format(c)
        return rstr
        #return self.pool.__str__()
    
    def __len__(self):
        return len(self.pool)

    def isEmpty(self):
        if len(self.pool) == 0:
            return True

        else:
            return False

    def size(self):
        return len(self.pool)        
    # try to pull the current "top" card out of the pool. used when moving a card to another
    # play area.
    # Return the card if successful.
    # Return False if unsuccessful (empty pool etc.)
    def pop(self):

        if len(self.pool) == 0:
            return False

        else:
            popcard = self.pool.pop(self.index)

            # if we pop off the last card in the pool,
            # need to show the previous one.
            if self.index > (len(self.pool) - 1):
                self.index -= 1

            return popcard
        
    # the action the player takes when finding more cards in the pool.
    # Return the value of the new "top" card in the pool.
    # Return False if pool is empty.
    # Note that this does not "pop" the card out - that is a separate operation.
    def advance(self):
        
        if len(self.pool) == 0:
            return False

        else:
            # TODO double-check this logic...
            if self.index == (len(self.pool) - 1):
                log.debug("Pool (size {}) exhausted. wrapping around".format(len(self.pool)))
                self.index = 0

            else:
                self.index += 1

            try:
                topcard = self.pool[self.index]
            except IndexError:
                print("pool.advance failed. index was {} and len of pool was {}".format(self.index, len(self.pool)))
                exit(5)
            return topcard


    # Show the top card in the pool.
    # TODO add "draw-three" support
    # Returns the value of the top card in the pool.
    # Returns False if the pool is empty.
    def showtop(self):

        if len(self.pool) == 0:
            return False

        else:
            topcard = self.pool[self.index]
            return topcard

# A Pile - I think these are more commonly known as tableaus.
class Pile(object):

    def __init__(self, pilecards, index):

        # hidden is a list of face-down cards at the bottom of the pile.
        # visible is a list of face-up cards at the top of the pile.
        # there should always be at least one visible card, unless the entire pile is empty.
        # cards should be moved from hidden to visible when visible is emptied.
        self.hidden = []
        self.visible = []
        # each pile has an index, used to differentiate piles
        self.index = index

        for card in pilecards:
            self.hidden.append(card)

        # make the topmost card visible.
        self.visible.append(self.hidden.pop())
        log.debug("created Pile instance with {} cards".format(len(self.hidden) + len(self.visible)))


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        rstr = ""
        for card in self.hidden:
            rstr += "[{}] ".format(str(card))
        for card in self.visible:
            rstr += "{} ".format(str(card))
        return rstr

    # Try to push a card onto the pile. 
    # Return True if successful.
    # Return False if card is not valid for pushing.
    def push(self, card):
        if self.canPush(card):
            self._dopush(card)
            return True
        else:
            return False

    def pushMany(self, cards):
        if len(cards) + len(self.visible) > 13:
            return False

        if self.canPush(cards[0]):
            self._dopush_many(cards)
            return True
        else:
            return False

    # Check to see if a card can be pushed onto the pile/stack.
    def canPush(self, card):
        if len(self.visible) == 0:

            # only a King can sit on top of a pile's visible cards.
            if card.rank == 13:
                return True
            else:
                return False

        # to add a card to a pile, the colour must not match the topmost card, and the rank must be one less than the topmost card.
        else:
            topcard = self.visible[-1]

            # Early exit due to colour mismatch. Stay fashion conscious!
            if card.colour == topcard.colour:
                return False
        
            if card.rank == (topcard.rank - 1):
                return True

            return False


    # "private" function to add a single card to the pile
    def _dopush(self, card):
        self.visible.append(card)

    # "private" function to add multiple cards to the pile
    def _dopush_many(self, cards):
        self.visible = self.visible + list(cards)

    # Try to pop out a card from the pile.
    # Return the card if successful
    # Return False if not successful
    def pop(self):
        if len(self.visible) == 0:
            return False

        else:
            card = self.visible.pop()
           
            # flip over a face-down card if there are no face-up cards in the pile
            if len(self.visible) == 0 and len(self.hidden) > 0:
                self.visible.append(self.hidden.pop())
            
            return card


    # Return the top card in the pile, but do not alter the pile.
    # Return false if pile is empty.
    def showTop(self):
        if len(self.visible) == 0:
            return False
        else:
            return self.visible[-1]

    # Return a tuple containing all of the visible cards in the pile.
    # Return false if pile is empty.
    def showAll(self):
        if len(self.visible) == 0:
            return False
        else:
            return tuple(self.visible)

    # Remove and return num cards from the visible pile.
    # Return false if there are not that many cards in the visible pile.
    def popMany(self, num):
        if num > len(self.visible):
            return False
        else:
            popped = []
            for i in range(0,num):
                popped.append(self.visible.pop())

            if len(self.visible) == 0 and len(self.hidden) > 0:
                self.visible.append(self.hidden.pop())

            return popped[::-1] # reverse list before returning


    # Return size (length) of the pile.
    def size(self):
        return len(self.hidden) + len(self.visible)

    # Return size (length) of visible cards in the pile.
    def visSize(self):
        return len(self.visible)

    # Return "topped-ness" of the pile.
    # A pile is "topped" if the first visible card is a King.
    def isTopped(self):
        if self.visible[0].rank == 13:
            return True
        else:
            return False

    # Return "bottomed-ness" of the pile.
    # A pile is "bottomed" if the last visible card is an Ace.
    def isBottomed(self):
        if self.visible[-1].rank == 1:
            return True
        else:
            return False


    # Return emptiness of the pile.
    def isEmpty(self):
        if len(self.visible) == 0:
            return True
        else:
            return False



# A card in a standard 52 card deck.
class Card(object):

    # TODO add some kind of mechanism to ensure there's only one instance
    # of each type of card in existence at any one time
    def __init__(self, index):

        if index < 1 or index > 52:
            raise ValueError("bad card index!")

        self.index = index
        rank = cards[index]['rank']

        if rank == 11:
            rank = "J"
        elif rank == 12:
            rank = "Q"
        elif rank == 13:
            rank = "K"
        else:
            rank = str(rank)

        # TODO add colours to this (how do colours work in python???)
        self.str = "{}{}".format(rank,cards[index]['suit'])
        self.rank = cards[index]['rank']
        self.suit = cards[index]['suit']
        self.colour = cards[index]['colour']
        self.name = cards[index]['name']

    def __str__(self):
        return self.str.__str__()

    def __repr__(self):
        return self.str.__repr__()


    
    # Return True if given card can stack on top of this card (in a stack).
    # Otherwise return False.
    def canStack(card):
        if self.rank == (card.rank + 1) and self.colour != card.colour:
            return True
        else:
            return False



# A solitaire game. Contains a deck, split among four collections, seven piles, and a pool.
class Solitaire(object):

    def __init__(self):
        mdeck = [Card(x) for x in range(1,53)]
        
        # always shuffle the deck.
        # is this random enough?
        random.shuffle(mdeck)

        log.debug("creating pool")
        poolc = []
        while len(poolc) < 24:
            poolc.append(mdeck.pop())
        self.pool = Pool(poolc)

        log.debug("creating collections")
        self.collections = []
        for i in range(1,5):
            self.collections.append(Collection(i))

        log.debug("creating piles")
        self.piles = []
        for i in range(1,8):
            #log.debug("creating a pile of size {}. {} cards left in the deck".format(i, len(mdeck)))
            pilec = []
            while len(pilec) != i:
                pilec.append(mdeck.pop())
            self.piles.append(Pile(pilec, i))
        log.debug("{} cards left in the deck to distribute.".format(len(mdeck)))
        
    def __str__(self):
        rstr = "Pool: {}\n{}\n".format(len(self.pool), str(self.pool))
        rstr += "\nCollections:\n"

        for coll in self.collections:
            rstr += "{}: {}\n".format(coll.index, str(coll))

        rstr += "\nPiles:\n"

        for pile in self.piles:
            rstr += "{}: {}\n".format(pile.index, pile)
        
        return rstr


    # use to check if the game is finished
    # be fast, not exhaustive: just make sure there are 52 cards in collections.
    def isComplete(self):
        return sum([c.size() for c in self.collections]) == 52
    
    # use to assert correctness in the game's current state.
    # return True if no issues found with game's state.
    # return False if any issues found.
    def invariant_check(self):

        # check number of cards in play
        cardcount = 0
        for p in self.piles:
            cardcount += p.size()
        for c in self.collections:
            cardcount += c.size()
        cardcount += self.pool.size()

        if cardcount != 52:
            log.error("Error: invariant check found {} cards in play".format(cardcount))
            return False


        # ensure only one instance of each card exists in the game
        cardindex = {}
        for i in range(1,53):
            cardindex[i] = 0

        for c in self.collections:
            for card in c.coll:
                cardindex[card.index] += 1

        for p in self.piles:
            for card in p.hidden:
                cardindex[card.index] += 1
            for card in p.visible:
                cardindex[card.index] += 1
        
        for card in self.pool.pool:
            cardindex[card.index] += 1

        for card in cardindex:
            if cardindex[card] != 1:
                log.error("Error: invariant check found {} instances of {} in play".format(cardindex[card],cards[card]['name']))
                print("1")
                return False

        # check validity of cards in collections - emptiness, one suit per collection, correct order
        collsuits = []
        for c in self.collections:
            oc = c.coll
            if c.isEmpty() and len(oc) != 0:
                print("2")
                return False

            if not c.isEmpty and len(oc) == 0:
                print("3")
                return False
           
            # collection only has one suit
            osuit = c.suit
            for card in c.showall():
                if card.suit != osuit:
                    print("4")
                    return False
            
            # suit appears once in all collections
            if osuit and osuit in collsuits:
                print("5")
                return False
            collsuits.append(osuit)
           
            # cards in collection have correct order
            for index, card in enumerate(c.coll):
                if card.rank != (index + 1):
                    print("6")
                    return False

        # check validity of piles - visible cards (tableau) have correct order of rank and alternating colour
        for p in self.piles:
            cards = p.showAll()
            if cards:
                if len(cards) == 1:
                    continue
                for index, card in enumerate(cards):
                    try:
                        ncard = cards[index + 1]
                    except IndexError:
                        continue
                    if card.rank != (ncard.rank + 1):
                        print("7")
                        return False
                    if ((card.colour == 'B' and ncard.colour != 'R') or (card.colour == 'R' and ncard.colour != 'B')):
                        return False


        return True

# lookup table of all the cards in a standard 52-card playing deck. Index is an integer because that's easy to work with.
cards = {
# Clubs
    1: {    'name': 'Ace of Clubs',
            'rank': 1,
            'colour': 'B',
            'suit': 'C'
        },
    2: {    'name': 'Two of Clubs',
            'rank': 2,
            'colour': 'B',
            'suit': 'C'
        },
    3: {    'name': 'Three of Clubs',
            'rank': 3,
            'colour': 'B',
            'suit': 'C'
        },
    4: {    'name': 'Four of Clubs',
            'rank': 4,
            'colour': 'B',
            'suit': 'C'
        },
    5: {    'name': 'Five of Clubs',
            'rank': 5,
            'colour': 'B',
            'suit': 'C'
        },
    6: {    'name': 'Six of Clubs',
            'rank': 6,
            'colour': 'B',
            'suit': 'C'
        },
    7: {    'name': 'Seven of Clubs',
            'rank': 7,
            'colour': 'B',
            'suit': 'C'
        },
    8: {    'name': 'Eight of Clubs',
            'rank': 8,
            'colour': 'B',
            'suit': 'C'
        },
    9: {    'name': 'Nine of Clubs',
            'rank': 9,
            'colour': 'B',
            'suit': 'C'
        },
    10: {   'name': 'Ten of Clubs',
            'rank': 10,
            'colour': 'B',
            'suit': 'C'
        },
    11: {   'name': 'Jack of Clubs',
            'rank': 11,
            'colour': 'B',
            'suit': 'C'
        },
    12: {   'name': 'Queen of Clubs',
            'rank': 12,
            'colour': 'B',
            'suit': 'C'
        },
    13: {   'name': 'King of Clubs',
            'rank': 13,
            'colour': 'B',
            'suit': 'C'
        },
# Spades
    14: {   'name': 'Ace of Spades',
            'rank': 1,
            'colour': 'B',
            'suit': 'S'
        },
    15: {   'name': 'Two of Spades',
            'rank': 2,
            'colour': 'B',
            'suit': 'S'
        },
    16: {   'name': 'Three of Spades',
            'rank': 3,
            'colour': 'B',
            'suit': 'S'
        },
    17: {   'name': 'Four of Spades',
            'rank': 4,
            'colour': 'B',
            'suit': 'S'
        },
    18: {   'name': 'Five of Spades',
            'rank': 5,
            'colour': 'B',
            'suit': 'S'
        },
    19: {   'name': 'Six of Spades',
            'rank': 6,
            'colour': 'B',
            'suit': 'S'
        },
    20: {   'name': 'Seven of Spades',
            'rank': 7,
            'colour': 'B',
            'suit': 'S'
        },
    21: {   'name': 'Eight of Spades',
            'rank': 8,
            'colour': 'B',
            'suit': 'S'
        },
    22: {   'name': 'Nine of Spades',
            'rank': 9,
            'colour': 'B',
            'suit': 'S'
        },
    23: {   'name': 'Ten of Spades',
            'rank': 10,
            'colour': 'B',
            'suit': 'S'
        },
    24: {   'name': 'Jack of Spades',
            'rank': 11,
            'colour': 'B',
            'suit': 'S'
        },
    25: {   'name': 'Queen of Spades',
            'rank': 12,
            'colour': 'B',
            'suit': 'S'
        },
    26: {   'name': 'King of Spades',
            'rank': 13,
            'colour': 'B',
            'suit': 'S'
        },
# Diamonds
    27: {   'name': 'Ace of Diamonds',
            'rank': 1,
            'colour': 'R',
            'suit': 'D'
        },
    28: {   'name': 'Two of Diamonds',
            'rank': 2,
            'colour': 'R',
            'suit': 'D'
        },
    29: {   'name': 'Three of Diamonds',
            'rank': 3,
            'colour': 'R',
            'suit': 'D'
        },
    30: {   'name': 'Four of Diamonds',
            'rank': 4,
            'colour': 'R',
            'suit': 'D'
        },
    31: {   'name': 'Five of Diamonds',
            'rank': 5,
            'colour': 'R',
            'suit': 'D'
        },
    32: {   'name': 'Six of Diamonds',
            'rank': 6,
            'colour': 'R',
            'suit': 'D'
        },
    33: {   'name': 'Seven of Diamonds',
            'rank': 7,
            'colour': 'R',
            'suit': 'D'
        },
    34: {   'name': 'Eight of Diamonds',
            'rank': 8,
            'colour': 'R',
            'suit': 'D'
        },
    35: {   'name': 'Nine of Diamonds',
            'rank': 9,
            'colour': 'R',
            'suit': 'D'
        },
    36: {   'name': 'Ten of Diamonds',
            'rank': 10,
            'colour': 'R',
            'suit': 'D'
        },
    37: {   'name': 'Jack of Diamonds',
            'rank': 11,
            'colour': 'R',
            'suit': 'D'
        },
    38: {   'name': 'Queen of Diamonds',
            'rank': 12,
            'colour': 'R',
            'suit': 'D'
        },
    39: {   'name': 'King of Diamonds',
            'rank': 13,
            'colour': 'R',
            'suit': 'D'
        },
# Hearts
    40: {   'name': 'Ace of Hearts',
            'rank': 1,
            'colour': 'R',
            'suit': 'H'
        },
    41: {   'name': 'Two of Hearts',
            'rank': 2,
            'colour': 'R',
            'suit': 'H'
        },
    42: {   'name': 'Three of Hearts',
            'rank': 3,
            'colour': 'R',
            'suit': 'H'
        },
    43: {   'name': 'Four of Hearts',
            'rank': 4,
            'colour': 'R',
            'suit': 'H'
        },
    44: {   'name': 'Five of Hearts',
            'rank': 5,
            'colour': 'R',
            'suit': 'H'
        },
    45: {   'name': 'Six of Hearts',
            'rank': 6,
            'colour': 'R',
            'suit': 'H'
        },
    46: {   'name': 'Seven of Hearts',
            'rank': 7,
            'colour': 'R',
            'suit': 'H'
        },
    47: {   'name': 'Eight of Hearts',
            'rank': 8,
            'colour': 'R',
            'suit': 'H'
        },
    48: {   'name': 'Nine of Hearts',
            'rank': 9,
            'colour': 'R',
            'suit': 'H'
        },
    49: {   'name': 'Ten of Hearts',
            'rank': 10,
            'colour': 'R',
            'suit': 'H'
        },
    50: {   'name': 'Jack of Hearts',
            'rank': 11,
            'colour': 'R',
            'suit': 'H'
        },
    51: {   'name': 'Queen of Hearts',
            'rank': 12,
            'colour': 'R',
            'suit': 'H'
        },
    52: {   'name': 'King of Hearts',
            'rank': 13,
            'colour': 'R',
            'suit': 'H'
        },
    # "wildcard" used because i'm a bad coder.
    53: {   'name': 'Joker',
            'rank': 999,
            'colour': 'G',
            'suit': 'J'
        }
}


# suits because i realise i didn't put that before
suits = {
    'C': {'name':   'Clubs',        'colour': 'B'},
    'S': {'name':   'Spades',       'colour': 'B'},
    'D': {'name':   'Diamonds',     'colour': 'R'},
    'H': {'name':   'Hearts',       'colour': 'R'}
}



