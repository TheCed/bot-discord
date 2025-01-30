import discord
import os
import shutil
import datetime
import asyncio
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("🚨 ERROR: No se encontró el token del bot. Asegúrate de configurarlo en Railway.")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

UPLOAD_FOLDER = "uploads"
EXTRA_FOLDER = "extra_uploads"
DEFAULT_NAME = "Modpack"
zip_name = DEFAULT_NAME

for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} está online.")

@bot.tree.command(name="nombre")
async def nombre(interaction: discord.Interaction, nuevo_nombre: str):
    global zip_name
    zip_name = nuevo_nombre
    await interaction.response.send_message(f"✅ Nombre del ZIP actualizado a: `{zip_name}`")

@bot.tree.command(name="subir")
async def subir(interaction: discord.Interaction):
    await interaction.response.defer()
    archivos = os.listdir(UPLOAD_FOLDER)
    
    if not archivos:
        await interaction.followup.send("⚠️ No hay archivos en `uploads` para comprimir.", ephemeral=True)
        return

    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    zip_path = f"{UPLOAD_FOLDER}/{zip_name} {fecha}.zip"

    try:
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)
        await interaction.followup.send(
            f"📁 Archivo ZIP `{zip_name} {fecha}.zip` generado.",
            file=discord.File(zip_path)
        )
    except Exception as e:
        await interaction.followup.send(f"🚨 Error al comprimir archivos: `{str(e)}`", ephemeral=True)

@bot.tree.command(name="resetear")
async def resetear(interaction: discord.Interaction):
    """Elimina todos los archivos en las carpetas de subida."""
    for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                os.remove(file_path)
            except Exception as e:
                await interaction.response.send_message(f"⚠️ No se pudo eliminar `{file}`: {str(e)}", ephemeral=True)
                return
    await interaction.response.send_message("🗑️ Todos los archivos han sido eliminados.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith((".dff", ".txd")):
                file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
                await attachment.save(file_path)
                await message.channel.send(f"✅ Archivo `{attachment.filename}` guardado correctamente.")
    
    await bot.process_commands(message)

async def main():
    async with bot:
        await bot.start(TOKEN)

try:
    asyncio.run(main())
except discord.errors.LoginFailure:
    print("🚨 ERROR: Token inválido. Revisa tu configuración en Railway.")
