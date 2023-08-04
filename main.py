import datetime
import time
from point_gestion import *
import dropbox
import json
import discord
from discord.ext import commands
from discord.ext.commands import Context


last_online_time = datetime.datetime.now()

guild = 610807410952634368
token = os.environ.get('TOKENcarre')
file = 'data.json'
dbToken = os.environ.get('TOKENdbcarre')
staff = 'ouioui'  # nom du rôle permettant les commande sup

defIntents = discord.Intents.default()
defIntents.presences = True
defIntents.members = True
defIntents.message_content = True

bot = commands.Bot('!', intents=defIntents)
bot.remove_command('help')


def has_role(role_name):
    print('hasrole')

    async def predicate(ctx):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        return role in ctx.author.roles

    return commands.check(predicate)


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user.name}")


@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000  # Convertir en millisecondes
    embed = discord.Embed(title='Pong!', description=f'temps de latence: {latency:.2f} ms',
                          color=discord.Color.brand_green())
    await ctx.send(embed=embed)


@bot.command()
async def mespoints(ctx: commands.Context):
    with open(file, 'r') as f:
        data = json.load(f)
    if str(ctx.author.id) not in data.keys():
        await ctx.send('vous avez 0 points')
    else:
        await ctx.send(f"vous avez {data[str(ctx.author.id)]} points")


@bot.command()
@has_role(staff)
async def rmpoints(ctx: Context, amount, target=None):
    try:
        member = ctx.guild.get_member(int(target))
    except ValueError:
        member = None
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
    elif not member:
        await ctx.send(f"aucun membre n'a l'id {target}")
    else:
        await ctx.send(f"le membre {member.nick if member.nick else member.global_name} a moins de {amount} points")


@bot.command()
@has_role(staff)
async def addpoints(ctx: commands.Context, amount=None, target=None):
    try:
        member = ctx.guild.get_member(int(target))
    except ValueError:
        await ctx.send(f"aucun membre n'a l'id {target}")
        return
    if not amount or not target or not amount.isdigit:
        await ctx.send(
            "il semble y avoir une erreure dans la syntaxe de la commande, utilisez !help pour plus d'information")
        return
    await ctx.send(
        f"{member.nick if member.nick else member.global_name} a désormais {add_points(file, int(target), int(amount))} points")


@bot.command()
@has_role(staff)
async def points(ctx: commands.Context, target: str):
    try:
        target = int(target)
        member = ctx.guild.get_member(target)
    except ValueError:
        await ctx.send('ID invalide')
        return
    with open(file, 'r') as f:
        pts = json.load(f).get(target, 0)

    nick = member.nick if member.nick else member.name
    await ctx.send(f"Le membre {nick} a {pts} points")


@bot.command()
@has_role(staff)
async def connectHour(ctx):
    await ctx.send(f'en ligne depuis le {last_online_time.strftime("%d/%m à %Hh%M")}')


@bot.command()
async def help(ctx: commands.Context):
    t = time.time()
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name='Liste des commandes')
    embed.add_field(name='!mespoints', value="affiche votre nombre de points", inline=False)
    embed.add_field(name='!aide', value="affiche ce message", inline=False)
    for role in ctx.bot.get_guild(guild).get_member(ctx.author.id).roles:
        if role.name == staff:
            embed.add_field(name='!rmpoints N ID',
                            value="retire N points au membre ayant l'id ID. si ID n'est pas précisé, cela retire "
                                  "N points a tous les membres present dans le canal (cette fonction est disponible uniquement dans les canaux vocaux)",
                            inline=False)
            embed.add_field(name='!addpoints N ID', value="ajoute N points au membre ayant l'id ID.", inline=False)
            embed.add_field(name='!connectHour', value="affiche le jour et l'heure de connection du bot", inline=False)
            embed.add_field(name='!points ID', value="affiche le nombre dde points de l'utilisateur ayant l'id ID",
                            inline=False)
    await ctx.author.send(embed=embed)
    print(time.time() - t)


bot.run(token)
