
import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv
import requests
import random
from database import get_champions_collection
import asyncio
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
        loading_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{name}_{number}.jpg"
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
        {"$push": {"owned_skins": {"skin": skin_name, "skin_image": loading_url}}}
        )

        new_skin_embed = discord.Embed(title=f"{skin_name}")
        new_skin_embed.set_image(url=skin_url) 
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

class BattleView(View):
    def __init__(self, challenger, opponent, challenger_champs, opponent_champs):
        super().__init__(timeout=300)
        self.challenger = challenger
        self.opponent = opponent
        self.challenger_champs = challenger_champs
        self.opponent_champs = opponent_champs
        self.accepted = False

    @discord.ui.button(label="✅ Aceitar Batalha", style=discord.ButtonStyle.success)
    async def accept_battle(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message("Apenas o desafiado pode aceitar a batalha!", ephemeral=True)
            return
        
        self.accepted = True
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Iniciar batalha
        await self.start_battle(interaction)

    async def start_battle(self, interaction):
        # Preparar campeões para batalha
        challenger_team = []
        opponent_team = []
        
        for champ in self.challenger_champs:
            challenger_team.append({
                'name': champ['name'],
                'hp': 20,
                'aura_level': champ.get('aura_level', 1),
                'owner': self.challenger.name,
                'image': champ.get('skin_image', champ.get('image', ''))
            })
        
        for champ in self.opponent_champs:
            opponent_team.append({
                'name': champ['name'],
                'hp': 20,
                'aura_level': champ.get('aura_level', 1),
                'owner': self.opponent.name,
                'image': champ.get('skin_image', champ.get('image', ''))
            })
        
        await interaction.followup.send("🔥 **BATALHA INICIADA!** 🔥")
        
        # Simular batalha por turnos
        round_num = 1
        while challenger_team and opponent_team:
            # Campeão atual de cada time
            challenger_champ = challenger_team[0]
            opponent_champ = opponent_team[0]
            
            # Criar embed do confronto principal
            embed = discord.Embed(
                title=f"⚔️ RODADA {round_num} ⚔️",
                color=0xff0000
            )

            embed.add_field(
                name=f"{challenger_champ['name']} ({self.challenger.name})",
                value=f"❤️ HP: {challenger_champ['hp']}/20\n🌟 Aura: {challenger_champ['aura_level']}",
                inline=True
            )

            embed.add_field(
                name="⚔️ VS ⚔️",
                value="━━━━━━━━━━",
                inline=True
            )

            embed.add_field(
                name=f"{opponent_champ['name']} ({self.opponent.name})",
                value=f"❤️ HP: {opponent_champ['hp']}/20\n🌟 Aura: {opponent_champ['aura_level']}",
                inline=True
            )

            await interaction.followup.send(embed=embed)
            
            # Criar embeds separados para as imagens lado a lado
            if challenger_champ['image'] and opponent_champ['image']:
                # Embed do challenger
                challenger_embed = discord.Embed(title=f"⚔️ {challenger_champ['name']}", color=0x0099ff)
                challenger_embed.set_image(url=challenger_champ['image'])
                
                # Embed do opponent
                opponent_embed = discord.Embed(title=f"🛡️ {opponent_champ['name']}", color=0xff9900)
                opponent_embed.set_image(url=opponent_champ['image'])
                
                # Enviar os dois embeds em sequência
                await interaction.followup.send(embed=challenger_embed)
                await interaction.followup.send(embed=opponent_embed)
            
            elif challenger_champ['image']:
                challenger_embed = discord.Embed(title=f"⚔️ {challenger_champ['name']}")
                challenger_embed.set_image(url=challenger_champ['image'])
                await interaction.followup.send(embed=challenger_embed)
            
            elif opponent_champ['image']:
                opponent_embed = discord.Embed(title=f"🛡️ {opponent_champ['name']}")
                opponent_embed.set_image(url=opponent_champ['image'])
                await interaction.followup.send(embed=opponent_embed)

            await asyncio.sleep(3)
            
            # Calcular dano
            challenger_damage = self.calculate_damage(challenger_champ['aura_level'])
            opponent_damage = self.calculate_damage(opponent_champ['aura_level'])
            
            # Aplicar dano
            challenger_champ['hp'] -= opponent_damage
            opponent_champ['hp'] -= challenger_damage
            
            # Criar embed dos resultados
            result_embed = discord.Embed(title="💥 Resultado do Turno", color=0xffa500)
            result_embed.add_field(
                name=f"{challenger_champ['name']}",
                value=f"Causou {challenger_damage} de dano\nHP restante: {max(0, challenger_champ['hp'])}/20",
                inline=True
            )
            result_embed.add_field(
                name="⚡",
                value="━━━━━━",
                inline=True
            )
            result_embed.add_field(
                name=f"{opponent_champ['name']}",
                value=f"Causou {opponent_damage} de dano\nHP restante: {max(0, opponent_champ['hp'])}/20",
                inline=True
            )
            
            await interaction.followup.send(embed=result_embed)
            
            # Verificar se alguém morreu
            deaths = []
            if challenger_champ['hp'] <= 0:
                deaths.append(f"💀 {challenger_champ['name']} foi derrotado!")
                challenger_team.pop(0)
            if opponent_champ['hp'] <= 0:
                deaths.append(f"💀 {opponent_champ['name']} foi derrotado!")
                opponent_team.pop(0)
            
            if deaths:
                death_embed = discord.Embed(title="💀 Campeão Derrotado!", description="\n".join(deaths), color=0x800080)
                await interaction.followup.send(embed=death_embed)
            
            await asyncio.sleep(3)
            round_num += 1
        
        # Determinar vencedor
        if challenger_team:
            winner = self.challenger
            winner_team = self.challenger_champs
            loser = self.opponent
            loser_champs = self.opponent_champs
            winner_name = self.challenger.name
        else:
            winner = self.opponent
            winner_team = self.opponent_champs
            loser = self.challenger
            loser_champs = self.challenger_champs
            winner_name = self.opponent.name
        
        # Embed final
        final_embed = discord.Embed(
            title="🏆 BATALHA FINALIZADA! 🏆",
            description=f"**{winner_name} VENCEU A BATALHA!**",
            color=0x00ff00
        )
        final_embed.add_field(name="Campeões sobreviventes", value=str(len(challenger_team if challenger_team else opponent_team)), inline=True)
        final_embed.add_field(name="Rodadas totais", value=str(round_num - 1), inline=True)
        
        await interaction.followup.send(embed=final_embed)
        
        # Atualizar banco de dados
        await self.update_database_after_battle(winner.id, winner_team, loser.id, loser_champs)
        

    def calculate_damage(self, aura_level):
        base_roll = random.randint(1, 20)
        
        # Bônus de aura (aumenta chance de valores altos)
        aura_bonus = {
            1: 0,
            2: 1,
            3: 2,
            4: 3,
            5: 4,
            6: 5
        }
        
        bonus = aura_bonus.get(aura_level, 0)
        
        # Chance de reroll com valor mais alto baseado na aura
        if bonus > 0 and random.randint(1, 10) <= bonus:
            second_roll = random.randint(1, 20)
            return max(base_roll, second_roll)
        
        return base_roll

    async def update_database_after_battle(self, winner_id, winner_champs, loser_id, loser_champs):
        champions_collection = get_champions_collection()
        
        # Deletar campeões do perdedor
        for champ in loser_champs:
            await champions_collection.delete_one({"user_id": loser_id, "name": champ['name']})
        
        # Atualizar campeões do vencedor com vitórias
        for champ in winner_champs:
            current_wins = champ.get('wins', 0)
            await champions_collection.update_one(
                {"user_id": winner_id, "name": champ['name']},
                {"$set": {"wins": current_wins + 1}}
            )

@bot.command()
async def battle(ctx, opponent: discord.Member):
    # if opponent.id == ctx.author.id:
    #     await ctx.send("Você não pode desafiar a si mesmo!")
    #     return
    
    if opponent.bot:
        await ctx.send("Você não pode desafiar um bot!")
        return
    
    champions_collection = get_champions_collection()
    
    # Verificar se o desafiante tem pelo menos 5 campeões
    challenger_champs = await champions_collection.find({"user_id": ctx.author.id}).to_list(length=100)
    if len(challenger_champs) < 5:
        await ctx.send("Você precisa ter pelo menos 5 campeões para batalhar!")
        return
    
    # Verificar se o oponente tem pelo menos 5 campeões
    opponent_champs = await champions_collection.find({"user_id": opponent.id}).to_list(length=100)
    if len(opponent_champs) < 5:
        await ctx.send(f"{opponent.name} precisa ter pelo menos 5 campeões para batalhar!")
        return
    
    # Selecionar os primeiros 5 campeões de cada jogador
    challenger_team = challenger_champs[:5]
    opponent_team = opponent_champs[:5]
    
    # Criar embed com informações da batalha
    embed = discord.Embed(title="⚔️ DESAFIO DE BATALHA! ⚔️", color=0xff0000)
    embed.add_field(name="Desafiante", value=ctx.author.name, inline=True)
    embed.add_field(name="Oponente", value=opponent.name, inline=True)
    embed.add_field(name="⚠️ AVISO", value="O perdedor terá seus 5 campeões deletados!", inline=False)
    
    challenger_names = "\n".join([f"• {champ['name']}" for champ in challenger_team])
    opponent_names = "\n".join([f"• {champ['name']}" for champ in opponent_team])
    
    embed.add_field(name=f"Time de {ctx.author.name}", value=challenger_names, inline=True)
    embed.add_field(name=f"Time de {opponent.name}", value=opponent_names, inline=True)
    
    view = BattleView(ctx.author, opponent, challenger_team, opponent_team)
    await ctx.send(f"{opponent.mention}, você foi desafiado para uma batalha!", embed=embed, view=view)

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
        "!battle <@oponente> - Desafia um usuário para uma batalha (5 campeões necessários)\n"
        "(apenas admin) !setAura <nome> <nível> - Define o nível de aura do campeão (1-5)\n"
    )
    await ctx.send(help_message)

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)