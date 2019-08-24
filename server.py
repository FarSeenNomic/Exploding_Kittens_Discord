import asyncio
from datetime import datetime
import pickle
import discord  #pip install pydiscord?
import gameObject

client = discord.Client()
game = gameObject.KittensGame()

def nocall():
    asyncio.sleep(1)

def log(strin):
    now = datetime.now()
    fi = open("logfile.log", "at")
    fi.write(now.strftime("%Y-%m-%d %H-%M-%S,") + str(strin) + "\n")
    fi.close()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print('------')

@client.event
async def on_message(message):
    global game
    if not message.content.startswith("!"):
        #message is not a command
        return
    elif message.author.bot:
        #message is made by a bot
        return

    elif message.content.startswith('!admin '): #runs code and echos to where it came from
        try:
            if len(message.content) >= 7 and game.isAdmin(message.author.id):
                evalStr = eval(message.content[7:])
                if evalStr is None:
                    await message.channel.send("Successful.")
                else:
                    await message.channel.send(evalStr)
                return
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))
            return

    elif message.content.startswith('!adminto '):   #runs code and echos to where the mention points
        try:
            if len(message.content) >= 9 and game.isAdmin(message.author.id):
                evalStr = eval(message.content[9:])
                if evalStr is None:
                    evalStr = "Successful."
                for person in message.mentions:
                    if (person.dm_channel is None):
                        await person.create_dm()
                    await person.dm_channel.send(evalStr)
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))
            return

    elif message.content.startswith('!save'):
        if game.isAdmin(message.author.id):
            pickle.dump(game, open("game.p", "wb"))
            await message.channel.send("Saved game.")
            return

    elif message.content.startswith('!load'):
        if game.isAdmin(message.author.id):
            game = pickle.load(open("game.p", "rb"))
            await message.channel.send("Loaded game.")
            return

    (personal, targeted) = game.do(
        message.content, message.author.id,
        message.author.name, message.channel.id
        )

    # personal always goes to the dm channel
    # targetted goes to whatever channel it was contacted by.

    if (personal is not None):
        if (message.author.dm_channel is None):
            await message.author.create_dm()
        await message.author.dm_channel.send(personal)
    if (targeted is not None):
        await message.channel.send(targeted)

client.run(open("TOKEN", "r").read().rstrip())
