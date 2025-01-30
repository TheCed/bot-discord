import discord
import os
import rarfile
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Inicializar bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Carpeta donde se guardarán los archivos
UPLOAD_FOLDER = "uploads"
RAR_FILE = "archivos_comprimidos.rar"

# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@bot.event
async def on_ready():
    print(f"{bot.user} está online y listo para recibir archivos.")

@bot.command()
async def subir(ctx):
    """Comprime los archivos subidos y envía el RAR"""
    rar_path = os.path.join(UPLOAD_FOLDER, RAR_FILE)
    
    with rarfile.RarFile(rar_path, "w") as rar:
        for file in os.listdir(UPLOAD_FOLDER):
            if file.endswith((".dff", ".txd")):
                rar.write(os.path.join(UPLOAD_FOLDER, file), file)
    
    await ctx.send("📁 Archivo RAR generado:", file=discord.File(rar_path))

@bot.event
async def on_message(message):
    """Recibe archivos y los guarda en la carpeta"""
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith((".dff", ".txd")):
                file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
                await attachment.save(file_path)
                await message.channel.send(f"✅ Archivo `{attachment.filename}` guardado.")
    
    await bot.process_commands(message)

# Ejecutar el bot
bot.run(TOKEN)
