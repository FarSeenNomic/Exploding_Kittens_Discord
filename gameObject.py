from random import randint
from datetime import timedelta
from datetime import datetime
import difflib
import csv      # for importing cards
from getAlpha import nextItemAlphabetical as nextPlayer
from getAlpha import lastItemAlphabetical as lastPlayer
import deckObj

def andMore(names):
    if len(names) == 0:
        return ''
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return names[0] + " and " + names[1]
    if len(names) == 3:
        return names[0] + ", " + names[1] + " and " + names[2]
    return names[0] + " and " + str(len(names)-1) + " more"

class KittensGame:
    def __init__(self):
        self.deck = deckObj.DeckKittens()        # hold all the main cards
        self.discard = deckObj.DeckKittens()     # holds the discards
        self.extraDeck = deckObj.DeckKittens()   # for funging
        self.playersQuitters = {}    # user.id : user.name
        self.playersAll = {}         # user.id : user.name
        self.playerCards = {}        # user.id : Deck
        self.playerStartTime = 0
        self.currentRoundNumber = 0
        self.playerCurrent = ""
        self.gameStarted = False
        self.allCardsUnique = []
        self.tellImplodingKitten = True
        self.turnsReversed = False
        self.admins = [
            269904594526666754,     #Imanton1, the devoloper
            #374911198010802179,    #Zen, leader of the Menagerie
            0
        ]
        self.channels = [
            595427470430437412,     #RYL nomic
            #601892112245719041,    #RYL bot-test
            614953375884115970,    #Menagerie nomic
            0
        ]

    def isAdmin(self, authorid):
        return authorid in self.admins or authorid == 269904594526666754

    def isRightChannel(self, cid):
        return cid in self.channels

    def isPlayer(self, authorid):
        return authorid in self.playersAll

    def isQuitter(self, authorid):
        return authorid in self.playersQuitters

    def do(self, messageContent, authorid, authorname, channelid):
        """
        takes a messageContent, authorid, authorname, and channelid
            messageContent is a string with the command
            authorid is a unique object that identifies a user
            authorname is a string used for alphabetizing and chatting to a user
            channelid is used for checking where the message is coming from
        returns None, or a string to send
        in the form [where, string]
        """
        if messageContent.startswith('!help'):
            return ("""(case sensitive)
!help
    displays this message
!enter
   Enters you to be eligable
!leave
   leaves the game, if the game has started, cannot return
!listPlayers
   Lists the currently playing players
!start (admin only)
   gives each player the starting hand, and shuffles the deck
!current
    displays the name of the current player
!time
    Sends a message of how long the current turn has been
!draw
   draws a card, send that card by DM
   makes note in the counter
!listCards
   DM's a list of your cards to you
!play <card>
   takes a card from your hand and puts it on the discard pile
!end
   ends your turn
!steal @player
    steals a random card from a player
!handSwap num num
    swaps the nth and nth card in your hand
!insert n card
    puts card card from your hand into position n in deck
    (0 is top, 1 is one card on top... -1 is bottom)
!admin/adminto (admin only)
    allows change to the python gamestate
""", "Help has been sent by DM to " + authorname)
        elif messageContent.startswith('!enter') and self.isRightChannel(channelid):
            if self.gameStarted and self.isQuitter(authorid):
                return (None, authorname + " has left and may not return.")
            else:
                if self.isPlayer(authorid):
                    return (None, authorname + " was already in.")
                else:
                    self.playersAll[authorid] = authorname
                    return (None, authorname + " has entered the game!")

        elif messageContent.startswith('!leave') and self.isRightChannel(channelid):
            if self.isPlayer(authorid):
                if self.gameStarted:
                    self.playersQuitters[authorid] = authorname
                self.playersAll.pop(authorid)
                return (None, authorname + " has left the game.")
            else:
                return (None, authorname + " is not a player.")

        elif messageContent.startswith('!listPlayers'):
            if len(self.playersAll) <= 3:
                strSend = "Players: "
            else:
                strSend = "("+str(len(self.playersAll))+"): "

            strSend += ", ".join(sorted(list(self.playersAll.values()), key=str.lower))
            return (None, strSend)

        elif messageContent.startswith('!start') and self.isRightChannel(channelid):
            if self.isAdmin(authorid):
                if self.gameStarted: return (None, "The game has already started.")
                if len(self.playersAll) == 0: return (None, "Zero players.")

                self.gameStarted = True

                with open('baseCards.txt', newline='') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    for row in spamreader:
                        self.allCardsUnique.append(row[1])
                        for count in range(int(row[0])):
                            self.deck.pushtop(row[1])
                self.deck.shuffle()
                # the deck is now initialized with cards

                # give players cards
                for pl in self.playersAll:
                    self.playerCards[pl] = deckObj.DeckKittens() #all players now have a blank deck
                    for count in range(7):
                        while self.deck.peek() == "Exploding Kitten":
                            self.deck.shuffle()

                        self.playerCards[pl].pushtop(self.deck.draw())
                    self.playerCards[pl].pushtop("Defuse")

                #it is the first players turn, so set them
                #and mark it on the clock
                self.playerCurrent = nextPlayer(list(self.playersAll.values()), "")
                self.playerStartTime = datetime.now()

                self.gameStarted = True
                return (None, "Now the game truly begins.")

        elif messageContent.startswith('!time') and self.isPlayer(authorid):
            if not self.gameStarted: return (None, "The game has not started.")
            return (None, timedelta(seconds=round((datetime.now() - self.playerStartTime).total_seconds())))

        elif messageContent.startswith('!draw') and self.isRightChannel(channelid) and self.isPlayer(authorid):
            if not self.gameStarted: return (None, "The game has not started.")
            cardDrawn = self.deck.draw()
            self.playerCards[authorid].pushtop(cardDrawn)
            if self.tellImplodingKitten and self.deck.peek() == "Imploding Kitten":
                publ = authorname + " drew a card\nThe next card is an Imploding Kitten!"
            else:
                publ = authorname + " drew a card (DM'd to you)"

            return ("You got a " + cardDrawn, publ)

        elif messageContent.startswith('!play') and self.isRightChannel(channelid) and self.isPlayer(authorid):
            if not self.gameStarted:
                return (None, "The game has not started.")
            try:
                guesses = difflib.get_close_matches(messageContent[6:], self.allCardsUnique)
                pick = guesses[0]
                for value in guesses:
                    if value in self.playerCards[authorid].cards:
                        pick = value
                        break

                if pick in self.playerCards[authorid].cards:
                    # if player has card
                    self.playerCards[authorid].cards.remove(pick)
                    self.discard.pushtop(pick)
                    return (None, authorname + " played a(n) '" + pick + "'")
                else:
                    return (None, "You do not have a(n) '" + pick + "'")
            except:
                return (None, "I do not know what a(n) '" + messageContent[6:] + "' is")

        elif messageContent.startswith('!end') and self.isRightChannel(channelid) and self.isPlayer(authorid):
            if not self.gameStarted:
                return (None, "The game has not started.")

            if self.playerCurrent != self.playersAll[authorid]:
                return (None, "It is not your turn.")

            if self.playerCurrent == max(list(self.playersAll.values())):
                self.currentRoundNumber += 1

            self.playerStartTime = datetime.now()
            if self.turnsReversed:
                self.playerCurrent = lastPlayer(list(self.playersAll.values()), self.playerCurrent)
            else:
                self.playerCurrent = nextPlayer(list(self.playersAll.values()), self.playerCurrent)

            playerID = list(self.playersAll)[list(self.playersAll.values()).index(self.playerCurrent)]

            return (None, "The new current player is now <@" + str(playerID) + ">")

        elif messageContent.startswith('!listCards') and self.isPlayer(authorid):
            return ("cards: " + ", ".join(self.playerCards[authorid].cards), None)

        elif messageContent.startswith('!current'):
            if not self.gameStarted: return (None, "The game has not started.")
            return (None, "The current player is " + self.playerCurrent)

#elif messageContent.startswith('!steal') and isRightChannel(channelid) and isPlayer(authorid):
#    if not self.gameStarted:
#        return (None, "The game has not started.")

#    if self.playerCurrent != self.playersAll[authorid]:
#        return (None, "It is not your turn.")

#    if len(message.mentions) != 1:
#        return (None, "You did not specify a person.")

#    if len(self.playerCards[message.mentions[0].id]) == 0:
#        return (None, "The person does not have enough cards.")

#    numOfCards = len(self.playerCards[message.mentions[0].id])
#    indexToSteal = randint(0, numOfCards-1)
#    self.playerCards[authorid].pushtop(
#       self.playerCards[message.mentions[0].id].cards.pop(indexToSteal))

#    return (None, authorname + " stole a card from " + message.mentions[0].name)
        elif messageContent.startswith('!handSwap') and self.isPlayer(authorid):
            args = messageContent.split(" ", 4)
            if len(args) != 3:
                return (None, "Wrong number of arguments: " + str(len(args) - 1) + " should be 3")
            # args[0] == '!handSwap'
            if not (args[1].isdigit() or (args[1].startswith('-') and args[1][1:].isdigit())):
                return (None, "The first argument is not an integer: " + args)

            if not (args[2].isdigit() or (args[2].startswith('-') and args[2][1:].isdigit())):
                return (None, "The second argument is not an integer: " + args)

            try:
                self.playerCards[authorid].swap(int(args[1]), int(args[2]))
                return (None, "swapped cards " + str(int(args[1])) + " and " + str(int(args[2])))
            except IndexError as e:
                return (None, "That index is outside the size of the list.")
            except Exception as e:
                print(repr(e))
                return (None, "oops, an error occured:\n"+str(repr(e)))

        elif messageContent.startswith('!insert ') and self.isPlayer(authorid):
            if not self.gameStarted:
                return (None, "The game has not started.")
            try:
                args = messageContent.split(" ", 3)
                # args[0] == '!insert'
                # args[1] == index
                # args[2] == card
                pick = difflib.get_close_matches(args[2], self.allCardsUnique)[0]
                # if player has card
                if pick in self.playerCards[authorid].cards:
                    self.playerCards[authorid].cards.remove(pick)
                    self.deck.insert(int(args[1]), pick)
                    return (None, authorname + " inserted a(n) '" + pick + "' into the deck.")
                else:
                    return (None, "You do not have a(n) '" + pick + "'")
            except Exception as e:
                return (None, "I do not know what a(n) '" + args[2] + "' is (error: "+repr(e)+")")
        return (None, None)
