
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
        aura_level = champ.get('aura_level')
        aura_label = champ.get('aura_label')
        if aura_level and aura_label:
            embed.add_field(name="", value=f"{aura_label} (Nível {aura_level})", inline=False)
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
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                await channel.send("Aurix aqui! Use '!help' para ver os comandos disponíveis. 😊")
                break
            except:
                continue
        break


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

    image = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion}_0.jpg"

    champion_data = {
        "user_id": ctx.author.id,
        "owner": ctx.author.name,
        "name": champion,
        "image": image
    }

    existent_champion = await champions_collection.find_one({"name": champion})
    if existent_champion:
        await ctx.send(f"o campeão {champion} já foi escolhido.")
        return

    embed = discord.Embed(title=champion)
    embed.set_image(url=image)
    
    class SaveChampView(View):
        def __init__(self, champion_data):
            super().__init__(timeout=60)
            self.champion_data = champion_data
            self.saved = False
        
        @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.success)
        async def save_champion(self, interaction: discord.Interaction, button: Button):
            if self.saved:
                await interaction.response.send_message("Campeão já foi salvo!", ephemeral=True)
                return
                
            await champions_collection.insert_one(self.champion_data)
            self.saved = True
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"Campeão {self.champion_data['name']} salvo com sucesso!", ephemeral=True)
    
    view = SaveChampView(champion_data)
    await ctx.send(embed=embed, view=view) 
    embed = discord.Embed(title=champion)


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
async def skin(ctx):
    champions_collection = get_champions_collection()
    user_champions = await champions_collection.find({"user_id": ctx.author.id}).to_list(length=100)
    if not user_champions:
        await ctx.send("Você não possui nenhum campeão.")
        await ctx.send("Use !champ para obter um campeão primeiro.")
        return
  
    chosen_champion = random.choice(user_champions)
    name = chosen_champion['name']
    
    await ctx.send(f"Campeão escolhido: {name}")
    await ctx.send(f"Adquirindo skin do campeão {name}...")
    
    champion = f"https://ddragon.leagueoflegends.com/cdn/15.14.1/data/en_US/champion/{name}.json"
    response = requests.get(champion)

    skins = response.json().get('data', {}).get(name, {}).get('skins', [])
    num_skins = len(skins)

    while True:
        number = random.randint(1, num_skins)
        skin_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{name}_{number}.jpg"
        new_skin = requests.get(skin_url)
        if new_skin.status_code == 200:
            break

    skin_name = skins[number]['name'] if number < len(skins) else "Unknown"
    
    if 'owned_skins' in chosen_champion:
        for s in chosen_champion['owned_skins']:
            if s['skin'] == skin_name:
                await ctx.send(f"Você já possui a skin '{skin_name}' para o campeão {name}.")
                return
            
    await champions_collection.update_one(
        {"user_id": ctx.author.id, "name": name},
        {"$push": {"owned_skins": {"skin": skin_name, "skin_image": skin_url}}}
    )

    new_skin_embed = discord.Embed(title=f"{skin_name}")
    new_skin_embed.set_image(url=skin_url)
    await ctx.send(embed=new_skin_embed)

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
async def search(ctx, name):
    champions_collection = get_champions_collection()
    existent_champion = await champions_collection.find_one({"name": name})
    if not existent_champion:
        await ctx.send("Este campeão ainda não foi encontrado.")
        return

    owner = existent_champion.get("owner", "Desconhecido")
    await ctx.send(f"Campeão {name} pertence ao usuário {owner}!")

@bot.command()
async def setAura(ctx, name, level):
    if ctx.author.id != 432174897473781771:
        await ctx.send("Você não tem permissão para usar este comando.")
        return
    champions_collection = get_champions_collection()
    existent_champion = await champions_collection.find_one({"name": name})
    if not existent_champion:
        await ctx.send("Este campeão ainda não foi encontrado.")
        return
    try:
        level = int(level)
        if level not in [1, 2, 3, 4, 5]:
            await ctx.send("Nível de aura inválido. Use um valor entre 1 e 5.")
            return
    except ValueError:
        await ctx.send("O nível de aura deve ser um número entre 1 e 5.")
        return

    owned_skins = existent_champion.get('owned_skins', [])
    if owned_skins:
        if level < 5:
            level += 1
        elif level == 5:
            level = 6

    aura_labels = {
        1: "Zero Aura",
        2: "Aura Fraca",
        3: "Aura Normal",
        4: "Aura Forte",
        5: "Muita Aura",
        6: "Aura Farming"
    }

    await champions_collection.update_one(
        {"name": name},
        {"$set": {"aura_level": level, "aura_label": aura_labels[level]}}
    )
    await ctx.send(f"Aura do campeão {name} definida para '{aura_labels[level]}' (nível {level}).")

@bot.command()
async def changeskin(ctx, name):
    champions_collection = get_champions_collection()
    existent_champion = await champions_collection.find_one({"user_id": ctx.author.id, "name": name})
    if not existent_champion:
        await ctx.send("Você não possui esse campeão.")
        return
    
    owned_skins = existent_champion.get('owned_skins', [])
    if not owned_skins:
        await ctx.send("Você não possui skins para este campeão.")
        return
    
    embed = discord.Embed(title=f"Escolha uma skin para {name}")
    for i, skin in enumerate(owned_skins):
        embed.add_field(name=f"{i+1}. {skin['skin']}", value="", inline=False)
    
    await ctx.send(embed=embed)
    await ctx.send("Digite o número da skin que você quer equipar:")
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        choice = int(msg.content) - 1
        
        if 0 <= choice < len(owned_skins):
            selected_skin = owned_skins[choice]
            await champions_collection.update_one(
                {"user_id": ctx.author.id, "name": name},
                {"$set": {"skin_image": selected_skin['skin_image']}}
            )
            await ctx.send(f"Skin '{selected_skin['skin']}' equipada para {name}!")
        else:
            await ctx.send("Número inválido.")
    except ValueError:
        await ctx.send("Por favor, digite um número válido.")
    except:
        await ctx.send("Tempo esgotado.")

@bot.command()
async def help(ctx):
    help_message = (
        "Comandos disponíveis:\n"
        "!ping - Responde com Pong!\n"
        "!champ - Escolhe um campeão aleatório do League of Legends\n"
        "!mychamps - Mostra os campeões escolhidos por você\n"
        "!delete <nome> - Deleta o campeão escolhido por você\n"
        "!skin - Adquire uma skin aleatória para um campeão aleatório\n"
        "!skins <nome> - Mostra as skins adquiridas para o campeão escolhido\n"
        "!search <nome> - Busca informações sobre um campeão\n"
        "!changeskin <nome> - Permite escolher uma skin para o campeão escolhido\n"
        "(apenas admin) !setAura <nome> <nível> - Define o nível de aura do campeão (1-5)\n"
    )
    await ctx.send(help_message)

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)