import datetime
import os
import dropbox
import json
import discord
from discord.ext import commands
from discord.ext.commands import Context

last_online_time = datetime.datetime.now()
token = os.environ.get('TOKENcarre')
roles = {'chef': 1136243683696574575, 'prof': 1136243683696574575, 'modo': 1136243683696574575,
         'staf': 1136243683696574575}
file = 'data.json'
dbToken = os.environ.get('TOKENdbcarre')

defIntents = discord.Intents.default()
defIntents.presences = True
defIntents.members = True
defIntents.message_content = True


def check_file_exists(filename):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, filename)
    if os.path.exists(file_path):
        return True


def create_json_file(filename):
    with open(filename, 'w') as f:
        json.dump({}, f)


# retourne 0 si le pseudo existe déjà
def add_pseudo(filename, pseudo, amount=0):
    with open(filename, 'r') as f:
        data = json.load(f)
        if pseudo in data:
            return 0
    data[pseudo] = amount
    with open(filename, 'w') as f:
        json.dump(data, f)


# retourne 0 si le pseudo n'existe pas
def remove_pseudo(filename, pseudo):
    with open(filename, 'r') as f:
        data = json.load(f)
    if pseudo in data:
        del data[pseudo]
    else:
        return 0
    with open(filename, 'w') as f:
        json.dump(data, f)


def add_points(filename, iD: int, amount: int):
    with open(filename, 'r') as f:
        data = json.load(f)
    if str(iD) in data.keys():
        data[str(iD)] += amount
        print(1)
    else:
        data[str(iD)] = amount
        print(2)
    with open(filename, 'w') as f:
        json.dump(data, f)
    return data[str(iD)]


def checkpoints(filename, listId, amount):
    with open(filename, 'r') as f:
        data = json.load(f)
    l1 = []
    l2 = data.keys()
    for iD in listId:
        if str(iD) not in l2 or data[str(iD)] - amount < 0:
            l1.append(iD)
    return l1


def remove_points(filename, iD, amount: int):
    iD = str(iD)
    with open(filename, 'r') as f:
        data = json.load(f)
    if iD in data:
        print(2)
        data[iD] -= amount
        print(3)
    else:
        return 0
    with open(filename, 'w') as f:
        print(5)
        json.dump(data, f)


def check_role(roleIdList, auth: discord.Member):
    for rl in roleIdList:
        for r in auth.roles:
            print(r.id, rl)
            if r.id == rl:
                print('membre identifié')
                return True
    return False


if not check_file_exists(file):
    create_json_file(file)

bot = commands.Bot('!', intents=defIntents)


def has_role(role_name):
    async def predicate(ctx):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        return role in ctx.author.roles
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user.name}")


@bot.command()
@has_role('ouioui')
async def rmpoints(ctx: Context, amount, target=None):
    if not check_role([roles['chef'], roles['prof']], ctx.message.author):
        await ctx.send("vous n'avez pas le rôle requis pour effectuer cette action")
    if target is None:
        vc = bot.get_channel(ctx.channel.id)
        if vc.__class__ != discord.VoiceChannel:
            await ctx.send("vous ne pouvez pas utiliser cette commande ici")
            return
        id_list = [member.id for member in vc.members]
        id_list.remove(ctx.author.id)
        print(id_list)
        li = checkpoints(file, id_list, int(amount))
        print(li)
        if not li:
            for i in id_list:
                print('rmpoint', i)
                remove_points(file, i, int(amount))
        else:
            nameList = []
            for i in li:
                nameList.append(bot.get_user(i).display_name)
            print(nameList)
            await ctx.send(f"le(s) membre(s) {','.join(nameList)} n'ont pas assez de points")
    elif not checkpoints(file, [target], int(amount)):
        remove_points(file, target, int(amount))
    elif not ctx.guild.get_member(int(target)):
        await ctx.send(f"aucun membre n'a l'id {target}")
    else:
        member = ctx.guild.get_member(int(target))
        await ctx.send(f"le membre {member.nick if member.nick else member.global_name} a moins de {amount} points")

@bot.command()
@has_role('ouioui')
async def addpoints(ctx: commands.Context, amount, target):
    if not check_role([roles['chef'], roles['modo']], ctx.message.author):
        await ctx.send("vous n'avez pas le rôle requis pour effectuer cette action")
    elif not ctx.guild.get_member(int(target)):
        await ctx.send(f"aucun membre n'a l'id {target}")
    else:
        member = ctx.guild.get_member(int(target))
        await ctx.send(
            f"{member.nick if member.nick else member.global_name} a désormais {add_points(file, int(target), int(amount))} points")


@bot.command()
async def mespoints(ctx: commands.Context):
    with open(file, 'r') as f:
        data = json.load(f)
    if str(ctx.author.id) not in data.keys():
        await ctx.send('vous avez 0 points')
    else:
        await ctx.send(f"vous avez {data[str(ctx.author.id)]} points")


@bot.command()
@has_role('ouioui')
async def points(ctx: commands.Context, target: str):
    if not check_role(list(roles.values()), ctx.author):
        await ctx.send("vous n'avez pas le rôle nécessaire pour effectuer cette action")
        return
    if not target.isdigit():
        await ctx.send('ID invalide')
        return
    member = ctx.guild.get_member(int(target))
    if member is None:
        await ctx.send('ID invalide')
        return
    with open(file, 'r') as f:
        pts = json.load(f).get(target, 0)

    nick = member.nick if member.nick else member.name
    await ctx.send(f"Le membre {nick} a {pts} points")


@bot.command()
@has_role('ouioui')
async def connectHour(ctx):
    await ctx.send(f'en ligne depuis le {last_online_time.strftime("%d/%m à %Hh%M")}')


@bot.command(help='vous affiche une description des commandes')
async def aide(ctx: commands.Context):
    if check_role([roles['staf']], ctx.author):
        pass
    await ctx.send("!rmpoint N ID   --> retire N points au membre ayant l'id ID. si ID n'est pas précisé, cela retire "
                   "N points a tous les membres present dans le canal (cette fonction est disponible uniquement dans les canaux vocaux)\n"
                   "-----------------------------------------------\n"
                   "!addpoints N ID --> ajoute N points au membre ayant l'id ID.\n"
                   "-----------------------------------------------\n "
                   "!connectHour    --> affiche le jour et l'heure de connection du bot\n"
                   "-----------------------------------------------\n ")
    await ctx.send(
        "!mespoints      --> affiche votre nombe de points\n"
        "-----------------------------------------------\n"
        "!points ID     --> affiche le nombre de points de l'utilisateur ayant l'id ID\n"
        "-----------------------------------------------\n"
        "!aide           --> affiche la liste des commandes avec leur description")


bot.run(token)
