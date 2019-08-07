#from random import getrandbits as randbool
from random import randint
from datetime import timedelta
from datetime import datetime
import asyncio
import pickle
import difflib
import csv      # for importing cards
#from shlex import split as parseLine
import discord
from getAlpha import nextItemAlphabetical as nextPlayer
from getAlpha import lastItemAlphabetical as lastPlayer
import deckObj

client = discord.Client()

deck = deckObj.DeckKittens()        # hold all the main cards
discard = deckObj.DeckKittens()     # holds the discards
extraDeck = deckObj.DeckKittens()   # for funging
playersQuitters = {}    # user.id : user.name
playersAll = {}         # user.id : user.name
playerCards = {}        # user.id : Deck
playerStartTime = 0
currentRoundNumber = 0
playerCurrent = ""
gameStarted = False
allCardsUnique = []
tellImplodingKitten = True
turnsReversed = False

def andMore(names):
    if len(names) == 0: return ''
    if len(names) == 1: return names[0]
    if len(names) == 2: return names[0] + " and " + names[1]
    if len(names) == 3: return names[0] + ", " + names[1] + " and " + names[2]
    return names[0] + " and " + str(len(names)-1) + " more"

def isAdmin(user):
    return user.id == 269904594526666754

def log(strin):
    now = datetime.now()
    fi = open("logfile.log", "at")
    fi.write(now.strftime("%Y-%m-%d %H-%M-%S,") + str(strin) + "\n")
    fi.close()

def isRightChannel(message):
    #return message.channel.id == 545368307570573324 or message.channel.id == 601892112245719041
    return message.channel.id == 595427470430437412

def isPlayer(message):
    global playersAll
    return message.author.id in playersAll

def isQuitter(message):
    global playersQuitters
    return message.author.id in playersQuitters

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print('------')

@client.event
async def on_message(message):
    global deck
    global discard
    global playersQuitters
    global playersAll
    global playerCards
    global playerStartTime
    global playerCurrent
    global gameStarted
    global currentRoundNumber
    global allCardsUnique
    global tellImplodingKitten
    global turnsReversed
    global extraDeck

    if not message.content.startswith("!"):
        #message is not a command
        return
    elif message.author.bot:
        #message is made by a bot
        return
    elif message.content.startswith('!help'):
        if (message.author.dm_channel is None): await message.author.create_dm()
        await message.author.dm_channel.send("""(case sensitive)
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
!time
    Sends a message of how long the current turn has been
!draw
   draws a card, send that card by DM
   makes note in the counter
!play <card>
   takes a card from your hand and puts it on the discard pile
!end
   ends your turn
!listCards
   DM's a list of your cards to you
!current
    displays the name of the current player
!steal @player
    steals a random card from a player
!handSwap num num
    swaps the nth and nth card in your hand
!insert n card
    puts card card from your hand into position n in deck
    (0 is top, 1 is one card on top... -1 is bottom)
!admin/adminto (admin only)
    allows change to the python gamestate
""")
    elif message.content.startswith('!enter') and isRightChannel(message):
        if gameStarted and isQuitter(message):
            await message.channel.send(message.author.name + " has left and may not return.")
        else:
            if isPlayer(message):
                await message.channel.send(message.author.name + " was already in.")
            else:
                playersAll[message.author.id] = message.author.name
                await message.channel.send(message.author.name + " has entered the game!")
                log("enter," + str(message.author.id))

    if message.content.startswith('!leave') and isRightChannel(message):
        if isPlayer(message):
            if gameStarted:
                playersQuitters[message.author.id] = message.author.name
            playersAll.pop(message.author.id)
            await message.channel.send(message.author.name + " has left the game.")
            log("left," + str(message.author.id))
        else:
            await message.channel.send(message.author.name + " is not a player.")

    elif message.content.startswith('!save'):
        if isAdmin(message.author):
            pickle.dump(deck, open("deckSave.p", "wb"))
            pickle.dump(discard, open("discardSave.p", "wb"))
            pickle.dump(playersQuitters, open("playersQuittersSave.p", "wb"))
            pickle.dump(playersAll, open("playersAllSave.p", "wb"))
            pickle.dump(playerCards, open("playerCardsSave.p", "wb"))
            pickle.dump(playerStartTime, open("playerStartTimeSave.p", "wb"))
            pickle.dump(playerCurrent, open("playerCurrentSave.p", "wb"))
            pickle.dump(gameStarted, open("gameStartedSave.p", "wb"))
            pickle.dump(currentRoundNumber, open("currentRoundNumberSave.p", "wb"))
            pickle.dump(allCardsUnique, open("allCardsUniqueSave.p", "wb"))
            pickle.dump(tellImplodingKitten, open("tellImplodingKittenSave.p", "wb"))
            pickle.dump(turnsReversed, open("turnsReversedSave.p", "wb"))
            pickle.dump(extraDeck, open("extraDeckSave.p", "wb"))
            
            await message.channel.send("Saved game.")

    elif message.content.startswith('!load'):
        if isAdmin(message.author):
            deck = pickle.load(open("deckSave.p", "rb"))
            discard = pickle.load(open("discardSave.p", "rb"))
            playersQuitters = pickle.load(open("playersQuittersSave.p", "rb"))
            playersAll = pickle.load(open("playersAllSave.p", "rb"))
            playerCards = pickle.load(open("playerCardsSave.p", "rb"))
            playerStartTime = pickle.load(open("playerStartTimeSave.p", "rb"))
            playerCurrent = pickle.load(open("playerCurrentSave.p", "rb"))
            gameStarted = pickle.load(open("gameStartedSave.p", "rb"))
            currentRoundNumber = pickle.load(open("currentRoundNumberSave.p", "rb"))
            allCardsUnique = pickle.load(open("allCardsUniqueSave.p", "rb"))
            tellImplodingKitten = pickle.load(open("tellImplodingKittenSave.p", "rb"))
            turnsReversed = pickle.load(open("turnsReversedSave.p", "rb"))
            extraDeck = pickle.load(open("extraDeckSave.p", "rb"))
            await message.channel.send("Loaded game.")

    elif message.content.startswith('!listPlayers'):
        strSend = "Players" + ("" if len(playersAll) <= 3 else "("+str(len(playersAll))+")")+ ": "
        strSend += ", ".join(list(playersAll.values()))
        await message.channel.send(strSend)

    elif message.content.startswith('!start') and isRightChannel(message) and isPlayer(message):
        if isAdmin(message.author):
            if gameStarted:
                await message.channel.send("The game has already started.")
                return
            if len(playersAll) == 0:
                await message.channel.send("Zero players.")
                return

            gameStarted = True

            with open('baseCards.txt', newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in spamreader:
                    allCardsUnique.append(row[1])
                    for count in range(int(row[0])):
                        deck.pushtop(row[1])
            deck.shuffle()                              # the deck is now initialized with cards

            for pl in playersAll:
                playerCards[pl] = deckObj.DeckKittens() #all players now have a blank deck
                for count in range(7):
                    playerCards[pl].pushtop(deck.draw())
                playerCards[pl].pushtop("Defuse")

            playerCurrent = nextPlayer(list(playersAll.values()), "")  #it is the first players turn, so set them
            playerStartTime = datetime()                   #and mark it on the clock

            # give players cards

            gameStarted = True
            await message.channel.send("Now the game truly begins.")
            log("start," + str(message.author.id))

    elif message.content.startswith('!time') and isPlayer(message):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return
        await message.channel.send(timedelta(seconds=round(datetime() - playerStartTime)))

    elif message.content.startswith('!draw') and isRightChannel(message) and isPlayer(message):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return
        cardDrawn = deck.draw()
        playerCards[message.author.id].pushtop(cardDrawn)
        if tellImplodingKitten and deck.peek() == "Imploding Kitten":
            await message.channel.send(message.author.name + " drew a card\nThe next card is an Imploding Kitten!")
        else:
            await message.channel.send(message.author.name + " drew a card (DM'd to you)")

        if (message.author.dm_channel is None): await message.author.create_dm()
        await message.author.dm_channel.send("You got a " + cardDrawn)

    elif message.content.startswith('!play') and isRightChannel(message) and isPlayer(message):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return
        try:
            guesses = difflib.get_close_matches(message.content[6:], allCardsUnique)
            pick = guesses[0]
            for value in guesses:
                if value in playerCards[message.author.id].cards:
                    pick = value
                    break

            if pick in playerCards[message.author.id].cards:
                # if player has card
                playerCards[message.author.id].cards.remove(pick)
                discard.pushtop(pick)
                await message.channel.send(message.author.name + " played a(n) '" + pick + "'")
            else:
                await message.channel.send("You do not have a(n) '" + pick + "'")
        except:
            await message.channel.send("I do not know what a(n) '" + message.content[6:] + "' is")

    elif message.content.startswith('!admin '): #runs code and echos to where it came from
        try:
            if len(message.content) >= 7 and isAdmin(message.author):
                evalStr = str(eval(message.content[7:]))
                if evalStr is None:
                    await message.channel.send("Successful.")
                await message.channel.send(evalStr)
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))

    elif message.content.startswith('!adminto '):   #runs code and echos to where the mention points
        try:
            if len(message.content) >= 9 and isAdmin(message.author) and len(message.mentions) == 1:
                if (message.mentions[0].dm_channel is None):
                    await message.mentions[0].create_dm()
                await message.mentions[0].dm_channel.send(eval(message.content[9:]))
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))

    elif message.content.startswith('!end') and isRightChannel(message) and isPlayer(message):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return

        if playerCurrent != playersAll[message.author.id]:
            await message.channel.send("It is not your turn.")
            return

        if playerCurrent == max(list(playersAll.values())):
            currentRoundNumber += 1

        playerStartTime = datetime()
        if turnsReversed:
            playerCurrent = nextPlayer(list(playersAll.values()), playerCurrent)
        else:
            playerCurrent = lastPlayer(list(playersAll.values()), playerCurrent)

        playerID = list(playersAll)[list(playersAll.values()).index(playerCurrent)]

        await message.channel.send("The new current player is now <@" + str(playerID) + ">")
        log("turnend," + str(message.author.id))

    elif message.content.startswith('!listCards') and isPlayer(message):
        if (message.author.dm_channel is None): await message.author.create_dm()
        await message.author.dm_channel.send(("cards: " + ", ".join(playerCards[message.author.id].cards))[:2000])

    elif message.content.startswith('!current'):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return
        await message.channel.send("The current player is " + playerCurrent)

    elif message.content.startswith('!steal') and isRightChannel(message) and isPlayer(message):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return

        if playerCurrent != playersAll[message.author.id]:
            await message.channel.send("It is not your turn.")
            return

        if len(message.mentions) != 1:
            await message.channel.send("You did not specify a person.")
            return

        if len(playerCards[message.mentions[0].id]) == 0:
            await message.channel.send("The person does not have enough cards.")
            return

        numOfCards = len(playerCards[message.mentions[0].id])
        indexToSteal = randint(0, numOfCards-1)
        playerCards[message.author.id].pushtop(playerCards[message.mentions[0].id].cards.pop(indexToSteal))

        await message.channel.send(message.author.name + " stole a card from " + message.mentions[0].name)

    elif message.content.startswith('!handSwap') and isPlayer(message):
        args = message.content.split(" ", 4)
        if len(args) != 3:
            await message.channel.send("Wrong number of arguments: " + str(len(args) - 1) + " should be 3")
            return
        # args[0] == '!handSwap'
        if not (args[1].isdigit() or (args[1].startswith('-') and args[1][1:].isdigit())):
            await message.channel.send("The first argument is not an integer: " + args)
            return

        if not (args[2].isdigit() or (args[2].startswith('-') and args[2][1:].isdigit())):
            await message.channel.send("The second argument is not an integer: " + args)
            return

        try:
            playerCards[message.author.id].swap(int(args[1]), int(args[2]))
            await message.channel.send("swapped cards " + str(int(args[1])) + " and " + str(int(args[2])))
        except IndexError as e:
            await message.channel.send("That index is outside the size of the list.")
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))

    elif message.content.startswith('!insert ') and isPlayer(message):
        if not gameStarted:
            await message.channel.send("The game has not started.")
            return
        try:
            args = message.content.split(" ", 3)
            # args[0] == '!insert'
            # args[1] == index
            # args[2] == card
            pick = difflib.get_close_matches(args[2], allCardsUnique)[0]
            # if player has card
            if pick in playerCards[message.author.id].cards:
                playerCards[message.author.id].cards.remove(pick)
                deck.insert(int(args[1]), pick)
                await message.channel.send(message.author.name + " inserted a(n) '" + pick + "' into the deck.")
            else:
                await message.channel.send("You do not have a(n) '" + pick + "'")
        except Exception as e:
            await message.channel.send("I do not know what a(n) '" + args[2] + "' is (error: " + repr(e) + ")")

client.run(open("token", "r").read())
