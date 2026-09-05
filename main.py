import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from datetime import datetime, time

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dicionário para armazenar configurações de "Bom dia"
goodmorning_config = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) sincronizado(s)")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")
    
    # Iniciar tarefa de bom dia
    if not goodmorning_task.is_running():
        goodmorning_task.start()

# ==================== COMANDOS DE MODERAÇÃO ====================

@bot.tree.command(name="kick", description="Remove um membro do servidor")
@app_commands.describe(membro="Membro a remover", razao="Razão do kick")
async def kick(interaction: discord.Interaction, membro: discord.Member, razao: str = "Nenhuma razão fornecida"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        return
    
    try:
        await membro.kick(reason=razao)
        embed = discord.Embed(
            title="⚠️ Membro Removido (KICK)",
            description=f"**Membro:** {membro.mention}\n**Razão:** {razao}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao remover membro: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Bane um membro do servidor")
@app_commands.describe(membro="Membro a banar", razao="Razão do ban")
async def ban(interaction: discord.Interaction, membro: discord.Member, razao: str = "Nenhuma razão fornecida"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        return
    
    try:
        await membro.ban(reason=razao)
        embed = discord.Embed(
            title="🚫 Membro Banido (BAN)",
            description=f"**Membro:** {membro.mention}\n**Razão:** {razao}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao banar membro: {e}", ephemeral=True)

@bot.tree.command(name="mute", description="Silencia um membro")
@app_commands.describe(membro="Membro a silenciar", razao="Razão do mute")
async def mute(interaction: discord.Interaction, membro: discord.Member, razao: str = "Nenhuma razão fornecida"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        return
    
    try:
        await membro.timeout(discord.utils.utcnow() + discord.Timedelta(hours=1), reason=razao)
        embed = discord.Embed(
            title="🔇 Membro Silenciado (MUTE)",
            description=f"**Membro:** {membro.mention}\n**Razão:** {razao}\n**Duração:** 1 hora",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao silenciar membro: {e}", ephemeral=True)

@bot.tree.command(name="unmute", description="Remove silêncio de um membro")
@app_commands.describe(membro="Membro a dessilenciar")
async def unmute(interaction: discord.Interaction, membro: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        return
    
    try:
        await membro.timeout(None)
        embed = discord.Embed(
            title="🔊 Membro Dessilenciado (UNMUTE)",
            description=f"**Membro:** {membro.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao dessilenciar membro: {e}", ephemeral=True)

@bot.tree.command(name="warn", description="Avisa um membro")
@app_commands.describe(membro="Membro a avisar", razao="Razão do aviso")
async def warn(interaction: discord.Interaction, membro: discord.Member, razao: str = "Nenhuma razão fornecida"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="⚠️ Aviso (WARN)",
        description=f"**Membro:** {membro.mention}\n**Razão:** {razao}",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)
    
    try:
        await membro.send(embed=embed)
    except:
        pass

@bot.tree.command(name="clear", description="Limpa mensagens do canal")
@app_commands.describe(quantidade="Número de mensagens a deletar (máx 100)")
async def clear(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        return
    
    if quantidade > 100:
        quantidade = 100
    
    try:
        deleted = await interaction.channel.purge(limit=quantidade)
        await interaction.response.send_message(f"✅ {len(deleted)} mensagens deletadas!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao limpar mensagens: {e}", ephemeral=True)

# ==================== COMANDO BOA DIA ====================

@bot.tree.command(name="setup_goodmorning", description="[ADMIN] Ativa bom dia automático em um canal")
@app_commands.describe(canal="Canal para enviar bom dia", hora="Hora (0-23)")
async def setup_goodmorning(interaction: discord.Interaction, canal: discord.TextChannel, hora: int):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Apenas o dono do servidor pode usar este comando!", ephemeral=True)
        return
    
    if not 0 <= hora <= 23:
        await interaction.response.send_message("❌ Hora deve ser entre 0 e 23!", ephemeral=True)
        return
    
    guild_id = interaction.guild.id
    goodmorning_config[guild_id] = {
        "canal_id": canal.id,
        "hora": hora
    }
    
    embed = discord.Embed(
        title="✅ Bom dia ativado!",
        description=f"**Canal:** {canal.mention}\n**Hora:** {hora}:00",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tasks.loop(minutes=1)
async def goodmorning_task():
    now = datetime.now()
    current_hour = now.hour
    
    for guild_id, config in goodmorning_config.items():
        if config["hora"] == current_hour and now.minute == 0:
            try:
                guild = bot.get_guild(guild_id)
                if guild:
                    canal = guild.get_channel(config["canal_id"])
                    if canal:
                        embed = discord.Embed(
                            title="🌅 Bom dia a todos!",
                            description="Tenha um ótimo dia! ☀️",
                            color=discord.Color.gold()
                        )
                        await canal.send(embed=embed)
            except Exception as e:
                print(f"Erro ao enviar bom dia: {e}")

# ==================== RESPONDER EM DM ====================

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="📩 Mensagem Recebida",
            description=f"**De:** {message.author.mention}\n**Mensagem:** {message.content}",
            color=discord.Color.blue()
        )
        
        try:
            app_info = await bot.application_info()
            owner = app_info.owner
            await owner.send(embed=embed)
            await message.reply("✅ Sua mensagem foi enviada para o desenvolvedor!", mention_author=False)
        except Exception as e:
            await message.reply(f"❌ Erro ao enviar mensagem: {e}", mention_author=False)
    
    await bot.process_commands(message)

# ==================== INICIAR BOT ====================

TOKEN = "SEU_TOKEN_AQUI"  # Substitua pelo seu token

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ Erro ao iniciar bot: {e}")
