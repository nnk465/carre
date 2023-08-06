import asyncio
import time
from point_gestion import *
import json
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands

# variables remplies dans la fonction on_ready
guild = None
last_online_time = None
namelist = []
namelist2 = []  # name list avec salon vocal pour la commande /rmpoints

# variables a remplir
infoDBChannel = 610807410952634372
guildName = 'mes bots'  # nom du serveur
token = os.environ.get('TOKENcarre')  # token bot discord
dbToken = os.environ.get('TOKENdbcarre')  # token bot dropbox
file = 'data.json'  # nom du fichier
can_add_points = ['ouioui']  # variables a remplir des noms de roles pour les commandes
can_rm_points = ['ouioui']
staff = ['ouioui']
waitT = 24 * 3600  # temps entre 2 sauvegarde du fichier file vers dropbox

# creation du bot
defIntents = discord.Intents.default()
defIntents.presences = True
defIntents.members = True
defIntents.message_content = True
bot = commands.Bot('/', intents=defIntents)
bot.remove_command('help')


# décorateur vérifiant une liste de rôle
def has_role(role_list):
    async def predicate(ctx: Context):
        for role in interaction.message.author.roles:
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
    global guild
    global last_online_time
    global namelist
    global namelist2
    t = time.time()
    print('on ready')
    last_online_time = datetime.now()  # set liqueured à laquelle le bot s'est mis en route
    guild = discord.utils.get(bot.guilds, name=guildName)
    for m in guild.members:  # set la liste des noms des membres
        namelist.append(m.name)
    namelist2 = namelist2
    namelist2.append('salon_vocale')
    print(f"Connecté en tant que {bot.user.name}\non ready en {time.time() - t} sec")
    bot.tree.copy_global_to(guild=bot.get_guild(610807410952634368))
    await bot.tree.sync(guild=bot.get_guild(610807410952634368))


#    await repeat_function()


async def autocompletion(interaction: discord.Interaction,
                         current: str):
    data = []
    key_list = []
    if interaction.command.name in ['hello', 'addpoints', 'info']:
        key_list = namelist
    if interaction.command.name == 'rmpoints':
        key_list = p
    for i in key_list:
        if i.lower().startswith(current.lower()):
            data.append(discord.app_commands.Choice(name=i, value=i))
    return data


@bot.tree.command()
async def ping(interaction: discord.Interaction):
    latency = bot.latency * 1000  # Convertir en millisecondes
    embed = discord.Embed(title='Pong!', description=f'temps de latence: {latency:.2f} ms',
                          color=discord.Color.brand_green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command()
async def mespoints(interaction: discord.Interaction):
    with open(file, 'r') as f:
        data = json.load(f)
        f.close()
    print(interaction.id)
    if str(interaction.user.id) not in data.keys():
        await interaction.response.send_message('vous avez 0 points', ephemeral=True)
    else:
        await interaction.response.send_message(f"vous avez {data[str(interaction.user.id)]} points", ephemeral=True)


@bot.tree.command()
@app_commands.autocomplete(name=autocompletion)
async def hello(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f'hello {name}', ephemeral=True)


@app_commands.autocomplete(name=autocompletion)
@bot.tree.command()
@has_role(can_rm_points)
async def rmpoints(interaction: discord.Interaction, nombre: str, name: str):
    if not nombre.isdigit():
        interaction.response.send_message("assurez vous que le nombre de points a retirer soit bien un nombre", ephemeral=True)
        return
    if name == 'salon_vocal':
        channel = interaction.channel
        if not isinstance(channel, discord.VoiceChannel):
            await interaction.response.send_message("vous ne pouvez pas utiliser cette commande ici", ephemeral=True)
            return
        id_list = [member.id for member in channel.members]
        id_list.remove(interaction.user.id)
        print(id_list)
        li = checkpoints(file, id_list, int(nombre))
        if li:
            print(li)
            nameList = [bot.get_user(i).display_name for i in li]
            await interaction.response.send_message(
                f"le(s) membre(s) {','.join(nameList)} ont moins de {nombre} points", ephemeral=True)
            return
        else:
            print('no', li)
            name_list = [member.display_name for member in channel.members]
            for i in id_list:
                remove_points(file, i, int(nombre))
                await interaction.response.send_message(f'les membres {name_list} ont été prélevé de {nombre} points', ephemeral=True)
                await interaction.channel.send(d)
                return
            await interaction.response.send_message("vous êtes tous seuls dans le salon...", ephemeral=True)
    member = interaction.guild.get_member_named(name)
    if member is None:
        await interaction.response.send_message(f"aucun membre n'a le nom {name}.", ephemeral=True)
        return
    else:
        iD = member.id
    if not checkpoints(file, [interaction.guild.get_member_named(name).id], int(nombre)):
        remove_points(file, iD, int(nombre))
        await interaction.response.send_message(f'le membre {member.name} a été prélevé de {nombre} points', ephemeral=True)
    else:
        await interaction.response.send_message(
            f"le membre {member.name} a moins de {nombre} points.", ephemeral=True)


@app_commands.autocomplete(name=autocompletion)
@bot.tree.command()
@has_role(staff)
async def addpoints(interaction: discord.Interaction, nombre: str, name: str):
    if not nombre.isdigit():
        await interaction.response.send_message(
            "assurez vous que le nombre de points a retirer soit bien un nombre", ephemeral=True)
        return
    if nombre.isdigit():
        member = interaction.guild.get_member_named(name)
        if member is None:
            await interaction.response.send_message(error_message_pseudo(name))
            return
        else:
            iD = member.id
            await interaction.response.send_message(
                f"{member.name} a désormais {add_points(file, iD, int(nombre))} points", ephemeral=True)
    else:
        await interaction.response.send_message(
            "il semble y avoir une erreur dans la syntaxe. utilisez !help pour plus d'information", ephemeral=True)


@app_commands.autocomplete(name=autocompletion)
@bot.tree.command()
@has_role(staff)
async def info(interaction: discord.Interaction, name: str):
    try:
        member = interaction.guild.get_member_named(name)
        iD = member.id
    except ValueError:
        await interaction.response.send_message(error_message_pseudo(name))
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
                    value=f'{pts} points\na rejoint le seveur le {member.joined_at.strftime("%d/%m à %H:%M")}\nrôles: {",".join([r.name for r in member.roles])}')
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command()
@has_role(staff)
async def bot_info(interaction: discord.Interaction):
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name='/bot_info')
    a = bot.application_info()
    print(a)
    avatar = bot.user.default_avatar.url
    print(avatar.__class__)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name='nom',
                    value=bot.user.name + f'\nen ligne depuis le {last_online_time.strftime("%d/%m à %Hh%M")}')

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command(name='del')
async def delete(interaction: discord.Interaction, n: str):
    if n.isdigit():
        history = ctx.channel.history(limit=int(n))
        async for message in history:
            await message.delete()
    else:
        await interaction.response.send_message('')


@bot.tree.command()
async def aide(interaction: discord.Interaction):
    roles = guild.get_member_named(interaction.user.name).roles
    embed = discord.Embed(colour=discord.Colour.teal())
    embed.set_author(name='Liste des commandes')
    embed.add_field(name='/mespoints', value="affiche votre nombre de points", inline=False)
    embed.add_field(name='/help', value="affiche ce message", inline=False)
    for role in roles:
        if role.name in can_rm_points:
            embed.add_field(name='/rmpoints N NAME',
                            value="retire N points au membre ayant le nom NAME. si NAME n'est pas précisé, cela retire "
                                  "N points a tous les membres present dans le canal (cette fonction est disponible uniquement dans les canaux vocaux)",
                            inline=False)
        if role.name in can_add_points:
            embed.add_field(name='/addpoints N NAME', value="ajoute N points au membre ayant le nom NAME.",
                            inline=False)
        if role.name in staff:
            embed.add_field(name='/connect_hour', value="affiche le jour et l'heure de connection du bot", inline=False)
            embed.add_field(name='/info NAME',
                            value="affiche le nombre dde points de l'utilisateur ayant le nom NAME",
                            inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.run(token)
