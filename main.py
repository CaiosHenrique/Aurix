import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

products = {}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    print(f'Mensagem recebida: {message.content}')

@bot.command()
async def monitor(ctx, link: str):
    products[link] = {'status': 'monitoring'}
    await ctx.send(f'Produto {link} está sendo monitorado.')

@bot.command()
async def products(ctx):
    if not products:
        await ctx.send('Nenhum produto monitorado.')
    else:
        response = 'Produtos monitorados:\n'
        for link, info in products.items():
            response += f'{link}: {info["status"]}\n'
        await ctx.send(response)

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run('MTM5Njk0NDY0OTIxNzc3MzYxOQ.GFy2dD.orRWhqFQzi9sxTsnbIpU-u2TpoxXVhesUwUn5s')