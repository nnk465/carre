import asyncio
import time
from point_gestion import *
import json
import discord
from discord.ext import commands
from discord.ext.commands import Context

# variables remplies dans la fonction on_ready
guildID = None
last_online_time = None

# variables a remplir
infoDBChannel = 610807410952634372
guildName = 'mes bots'  # nom du serveur
token = os.environ.get('TOKENcarre')  # token bot discord
dbToken = os.environ.get('TOKENdbcarre')  # token bot dropbox
file = 'data.json'  # nom du fichier
can_add_points = ['ouioui']
can_rm_points = ['ouioui']
staff = ['ouioui']  # nom du rôle permettant les commandes speciales
waitT = 24 * 3600  # temps entre 2 sauvegarde du fichier file vers dropbox

# creation du bot
defIntents = discord.Intents.default()
defIntents.presences = True
defIntents.members = True
defIntents.message_content = True
bot = commands.Bot('!', intents=defIntents)
bot.remove_command('help')


# décorateur vérifiant une liste de rôle
def has_role(role_list):
    async def predicate(ctx: Context):
        for role in ctx.author.roles:
            if role.name in role_list:
                return True
        return False

    return commands.check(predicate)


async def repeat_function():
    while True:
        await upload(bot.get_channel(infoDBChannel), dbToken, file)
        await asyncio.sleep(waitT)


@bot.event
async def on_ready():
    global guildID
    global last_online_time
    last_online_time = datetime.now()  # set liqueured à laquelle le bot s'est mis en route
    print(f"Connecté en tant que {bot.user.name}")
    guildID = discord.utils.get(bot.guilds, name=guildName).id

#    await repeat_function()


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
        f.close()
    if str(ctx.author.id) not in data.keys():
        await ctx.send('vous avez 0 points')
    else:
        await ctx.send(f"vous avez {data[str(ctx.author.id)]} points")


@bot.command()
@has_role(can_rm_points)
async def rmpoints(ctx: Context, amount, target=None):
    try:
        member = ctx.guild.get_member_named(target)
        iD = member.id
    except ValueError:
        await ctx.send(f"aucun membre n'a le nom {target}.")
        return
    if target is None:
        channel = bot.get_channel(ctx.channel.id)
        if not isinstance(channel, discord.VoiceChannel):
            await ctx.send("vous ne pouvez pas utiliser cette commande ici")
            return
        id_list = [member.id for member in channel.members]
        id_list.remove(ctx.author.id)
        li = checkpoints(file, id_list, int(amount))
        if li:
            nameList = [bot.get_user(i).display_name for i in li]
            await ctx.send(f"le(s) membre(s) {','.join(nameList)} ont moins de {amount} points")
        else:
            name_list = [member.display_name for member in channel.members]
            for i in id_list:
                remove_points(file, i, int(amount))
                await ctx.send(f'les membres {name_list} ont été prélevé de {amount} points')
                return
    elif not checkpoints(file, [name_to_iD(target)], int(amount)):
        remove_points(file, iD, int(amount))
        await ctx.send(f'le membre {member.name} a été prélevé de {amount} points')
    else:
        await ctx.send(
            f"le membre {member.name} a moins de {amount} points.")


@bot.command()
@has_role(staff)
async def addpoints(ctx: commands.Context, amount=None, target=None):
    if target is None or amount is None:
        await ctx.send("il semble y avoir une erreur dans la syntaxe. utilisez !help pour plus d'information")
        return
    if amount.isdigit():
        member = ctx.guild.get_member_named(target)
        if member is None:
            await ctx.send(error_message_pseudo(target))
            return
        else:
            iD = member.id
            await ctx.send(
                f"{member.name} a désormais {add_points(file, iD, int(amount))} points")
    else:
        await ctx.send("il semble y avoir une erreur dans la syntaxe. utilisez !help pour plus d'information")


@bot.command()
@has_role(staff)
async def info(ctx: commands.Context, target):
    try:
        member = ctx.guild.get_member_named(target)
        iD = member.id
    except ValueError:
        await ctx.send(error_message_pseudo(target))
        return
    with open(file, 'r') as f:
        pts = json.load(f).get(iD, 0)
        f.close()
    print(bot.guilds)
    nick = member.nick if member.nick else member.name
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name='!points')
    embed.set_thumbnail(url=member.default_avatar.url)
    embed.add_field(name=nick,
                    value=f'{pts} points\na rejoint le seveur le {member.joined_at.strftime("%d/%m à %H:%M")}')
    await ctx.send(embed=embed)


@bot.command()
@has_role(staff)
async def connectHour(ctx):
    await ctx.send(f'en ligne depuis le {last_online_time.strftime("%d/%m à %Hh%M")}')


@bot.command()
async def help(ctx: commands.Context):
    roles = bot.get_guild(guildID).get_member_named(ctx.author.name).roles
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name='Liste des commandes')
    embed.add_field(name='!mespoints', value="affiche votre nombre de points", inline=False)
    embed.add_field(name='!aide', value="affiche ce message", inline=False)
    for role in roles:
        if role.name in can_rm_points:
            embed.add_field(name='!rmpoints N NAME',
                            value="retire N points au membre ayant le nom NAME. si NAME n'est pas précisé, cela retire "
                                  "N points a tous les membres present dans le canal (cette fonction est disponible uniquement dans les canaux vocaux)",
                            inline=False)
        if role.name in can_add_points:
            embed.add_field(name='!addpoints N NAME', value="ajoute N points au membre ayant le nom NAME.",
                            inline=False)
        if role.name in staff:
            embed.add_field(name='!connectHour', value="affiche le jour et l'heure de connection du bot", inline=False)
            embed.add_field(name='!points NAME',
                            value="affiche le nombre dde points de l'utilisateur ayant le nom NAME",
                            inline=False)
    await ctx.author.send(embed=embed)


bot.run(token)
