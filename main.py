
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
import random
from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI')
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['Aurix_db']

try:
    mongo_client.admin.command('ping')
    print("Conexão com o MongoDB estabelecida com sucesso!")
except Exception as e:
    print(f"Falha ao conectar ao MongoDB: {e}")

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def champ(ctx):
    url = "https://ddragon.leagueoflegends.com/cdn/15.14.1/data/en_US/champion.json"
    champions = requests.get(url)

    data = champions.json()
    champion_names = [champ['name'] for champ in data['data'].values()]
    
    champion = random.choice(champion_names)

    if champion == "Nunu & Willump": champion = "Nunu"
    if " " in champion:
        champion = champion.replace(" ", "")
    elif "'" in champion:
        if champion not in "Kog'Maw":
            idx = champion.find("'")
            if idx != -1 and idx + 1 < len(champion):
                champion = champion[:idx+1] + champion[idx+1].lower() + champion[idx+2:]
    champion = champion.replace("'", "")

    image = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion}_0.jpg"

    if not hasattr(bot, "user_champions"):
        bot.user_champions = {}
    bot.user_champions[ctx.author.id] = {"id": ctx.author.id, "name": champion, "image": image}

    await ctx.send(image)

@bot.command()
async def mychamps(ctx):
    if not hasattr(bot, "user_champions") or ctx.author.id not in bot.user_champions:
        await ctx.send("Você ainda não escolheu um campeão. Use !c para escolher.")
        return
    champions = bot.user_champions[ctx.author.id]
    print("meus campeões:", champions)

    champion_name = champions["name"]
    champion_image = champions["image"]

    await ctx.send(f"Seu campeão é: {champion_name}")
    await ctx.send(champion_image)

    
@bot.command()
async def h(ctx):
    help_message = (
        "Comandos disponíveis:\n"
        "!ping - Responde com Pong!\n"
        "!champ - Escolhe um campeão aleatório do League of Legends e envia a imagem\n"
        "!mychamps - Mostra o campeão escolhido por você\n"
    )
    await ctx.send(help_message)

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)