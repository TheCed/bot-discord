import discord
import os
import shutil
from discord.ext import commands

# Obtener el token desde las variables de entorno
TOKEN = os.environ.get("DISCORD_TOKEN")

# Verificar que el token esté disponible
if not TOKEN:
    raise ValueError("\ud83d\udea8 ERROR: No se encontró el token del bot. Asegúrate de configurarlo en Railway.")

# Imprimir el token para debug (¡Elimina esta línea después de verificar!)
print(f"\ud83d\udd0d Token detectado: {TOKEN}")

# Configurar intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Inicializar bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Carpeta donde se guardarán los archivos
UPLOAD_FOLDER = "uploads"
RAR_FILE = "Modpack SKINS dd/mm/yyyy"

# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@bot.event
async def on_ready():
    print(f"\u2705 {bot.user} está online y listo para recibir archivos.")

@bot.command()
async def subir(ctx):
    """Comprime los archivos subidos y envía el ZIP"""
    zip_path = f"{UPLOAD_FOLDER}/{RAR_FILE}.zip"
    
    # Comprimir archivos en ZIP
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)
    
    await ctx.send("\ud83d\udcc1 Archivo ZIP generado:", file=discord.File(zip_path))

@bot.event
async def on_message(message):
    """Recibe archivos y los guarda en la carpeta"""
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith((".dff", ".txd")):
                file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
                await attachment.save(file_path)
                await message.channel.send(f"\u2705 Archivo `{attachment.filename}` guardado correctamente.")
    
    await bot.process_commands(message)

# Ejecutar el bot
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    print("\ud83d\udea8 ERROR: Token inválido. Revisa tu configuración en Railway.")
