import os
import discord
from discord.ext import commands
import json


file = 'data.json'
staff_role = 'ouioui'
token = os.environ.get('TOKENcarre')

def check_file_exists(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)

def add_pseudo(filename, pseudo, amount=0):
    with open(filename, 'r') as f:
        data = json.load(f)
    if pseudo not in data:
        data[pseudo] = amount
        with open(filename, 'w') as f:
            json.dump(data, f)
        return 1
    return 0

def remove_pseudo(filename, pseudo):
    with open(filename, 'r') as f:
        data = json.load(f)
    if pseudo in data:
        del data[pseudo]
        with open(filename, 'w') as f:
            json.dump(data, f)
        return 1
    return 0

def add_points(filename, iD: int, amount: int):
    with open(filename, 'r') as f:
        data = json.load(f)
    data[str(iD)] = data.get(str(iD), 0) + amount
    with open(filename, 'w') as f:
        json.dump(data, f)
    return data[str(iD)]

def remove_points(filename, iD, amount: int):
    with open(filename, 'r') as f:
        data = json.load(f)
    if str(iD) in data:
        data[str(iD)] = max(0, data[str(iD)] - amount)
        with open(filename, 'w') as f:
            json.dump(data, f)
        return 1
    return 0

def checkpoints(filename, listId, amount):
    with open(filename, 'r') as f:
        data = json.load(f)
    return [iD for iD in listId if str(iD) not in data or data[str(iD)] < amount]

def has_role(role_name):
    def predicate(ctx):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        return role in ctx.author.roles
    return commands.check(predicate)

bot = commands.Bot('!')

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user.name}")

@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000
    embed = discord.Embed(title='Pong!', description=f'Temps de latence: {latency:.2f} ms', color=discord.Color.brand_green())
    await ctx.send(embed=embed)

# Reste de vos commandes...
# ...

bot.run(token)
