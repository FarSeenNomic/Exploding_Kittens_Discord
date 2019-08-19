import deckObj
import discord  #pip install pydiscord?
import asyncio
import gameObject

client = discord.Client()
game = gameObject()


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

    elif messageContent.startswith('!admin '): #runs code and echos to where it came from
        try:
            if len(messageContent) >= 7 and isAdmin(authorid):
                evalStr = str(eval(messageContent[7:]))
                if evalStr is None:
                    await message.channel.send("Successful.")
                else:
                    await message.channel.send(evalStr)
                return
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))
            return

    elif messageContent.startswith('!adminto '):   #runs code and echos to where the mention points
        try:
            if len(messageContent) >= 9 and isAdmin(authorid) and len(message.mentions) == 1:
                if (message.mentions[0].dm_channel is None):
                    await message.mentions[0].create_dm()
                await message.mentions[0].dm_channel.send(eval(messageContent[9:]))
        except Exception as e:
            print(repr(e))
            await message.channel.send("oops, an error occured:\n"+str(repr(e)))
            return

    elif messageContent.startswith('!save'):
        if isAdmin(authorid):
            pickle.dump(game, open("game.p", "wb"))
            await message.channel.send("Loaded game.")
            return

    elif messageContent.startswith('!load'):
        if isAdmin(authorid):
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
        if (message.author.dm_channel is None): await message.author.create_dm()
        await message.author.dm_channel.send(personal)
    if (targeted is not None):
        await message.channel.send(targeted)

client.run(open("TOKEN", "r").read().rstrip())
