
import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv
import requests
import random
from database import get_champions_collection
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

class ChampView(View):
    def __init__(self, champs):
        super().__init__(timeout=60)
        self.champs = champs
        self.index = 0

    async def update_message(self, interaction):
        champ = self.champs[self.index]
        embed = discord.Embed(title=champ.get('name', ''))
        if 'image' in champ and 'skin_image' not in champ:
            embed.set_image(url=champ['image'])
        elif 'skin_image' in champ:
            embed.set_image(url=champ['skin_image'])
        await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.index = (self.index - 1) % len(self.champs)
        await self.update_message(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.index = (self.index + 1) % len(self.champs)
        await self.update_message(interaction)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Comando Irreconhecido ou erro")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def champ(ctx):
    champions_collection = get_champions_collection()
    url = "https://ddragon.leagueoflegends.com/cdn/15.14.1/data/en_US/champion.json"
    champions = requests.get(url)

    data = champions.json()
    champion_names = [champ['name'] for champ in data['data'].values()]
    
    while True:
        champion = random.choice(champion_names)
        
        existing_champion = await champions_collection.find_one({"name": champion})
        if not existing_champion:
            break

    if champion == "Nunu & Willump": champion = "Nunu"
    if " " in champion:
        champion = champion.replace(" ", "")
    elif "'" in champion:
        if champion not in "Kog'Maw":
            idx = champion.find("'")
            if idx != -1 and idx + 1 < len(champion):
                champion = champion[:idx+1] + champion[idx+1].lower() + champion[idx+2:]
    champion = champion.replace("'", "")

    image = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion}_0.jpg"

    champion_data = {
        "user_id": ctx.author.id,
        "name": champion,
        "image": image
    }

    existent_champion = await champions_collection.find_one({"name": champion})
    if existent_champion:
        await ctx.send(f"o campeão {champion} já foi escolhido.")
        return

    await champions_collection.insert_one(champion_data)
    await ctx.send(image)

@bot.command()
async def mychamps(ctx):
    champions_collection = get_champions_collection()
    champions = await champions_collection.find({"user_id": ctx.author.id}).to_list(length=100)
    if not champions:
        await ctx.send("Você ainda não escolheu um campeão.")
        return

    champ = champions[0]
    embed = discord.Embed(title=champ['name'])
    embed.set_image(url=champ['image'])

    await ctx.send(embed=embed, view=ChampView(champions))

@bot.command()
async def delete(ctx, name):
    champions_collection = get_champions_collection()
    result = await champions_collection.delete_one({"user_id": ctx.author.id, "name": name})
    if result.deleted_count > 0:
        await ctx.send(f"Campeão {name} deletado com sucesso!")
    else:
        await ctx.send(f"Campeão {name} não encontrado.")

@bot.command()
async def skin(ctx, name):
    champions_collection = get_champions_collection()
    existent_champion = await champions_collection.find_one({"user_id": ctx.author.id, "name": name})
    if not existent_champion:
        await ctx.send("Voce nao possui esse campeao.")
        await ctx.send("Use !mychamps para ver seus campeões.")
        return
    
    champion = f"https://ddragon.leagueoflegends.com/cdn/15.14.1/data/en_US/champion/{name}.json"
    response = requests.get(champion)

    skins = response.json().get('data', {}).get(name, {}).get('skins', [])
    num_skins = len(skins)

    await ctx.send(f"Adquirindo skin do campeão {name}...")
    while True:
        number = random.randint(1, num_skins)
        skin_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{name}_{number}.jpg"
        new_skin = requests.get(skin_url)
        print("Status code:", new_skin.status_code)
        if new_skin.status_code == 200:
            break

    skin_name = skins[number]['name'] if number < len(skins) else "Unknown"
    if 'owned_skins' in existent_champion:
        for s in existent_champion['owned_skins']:
            if s['skin'] == skin_name:
                await ctx.send(f"Você já possui a skin '{skin_name}' para o campeão {name}.")
                return
            
    await champions_collection.update_one(
            {"user_id": ctx.author.id, "name": name},
            {"$push": {"owned_skins": {"skin": skin_name, "skin_image": skin_url}}}
        )

    new_skin = discord.Embed(title=f"{skin_name}")
    new_skin.set_image(url=skin_url)
    await ctx.send(embed=new_skin)

@bot.command()
async def skins(ctx, name):
    champions_collection = get_champions_collection()
    existent_champion = await champions_collection.find_one({"user_id": ctx.author.id, "name": name})
    if not existent_champion:
        await ctx.send("Você não possui esse campeão.")
        await ctx.send("Use !mychamps para ver seus campeões.")
        return
    
    skins = existent_champion.get('owned_skins', [])
    if not skins:
        await ctx.send("Você não possui skins para este campeão.")
        return
    
    embed = discord.Embed(title=f"Skins do campeão {name}")
    embed.set_image(url=existent_champion['skin_image'])

    await ctx.send(embed=embed, view=ChampView(skins))


@bot.command()
async def help(ctx):
    help_message = (
        "Comandos disponíveis:\n"
        "!ping - Responde com Pong!\n"
        "!champ - Escolhe um campeão aleatório do League of Legends e envia a imagem\n"
        "!mychamps - Mostra o campeão escolhido por você\n"
        "!delete <nome> - Deleta o campeão escolhido por você\n"
        "!skin <nome> - Adquire uma skin aleatória para o campeão escolhido\n"
        "!skins <nome> - Mostra as skins adquiridas para o campeão escolhido\n"
    )
    await ctx.send(help_message)

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)