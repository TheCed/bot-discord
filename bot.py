import discord
import os
import shutil
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Verificar que el token esté disponible
if not TOKEN:
    raise ValueError("🚨 ERROR: No se encontró el token del bot. Asegúrate de configurarlo en las variables de entorno.")

# Configurar intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Inicializar bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Carpeta donde se guardarán los archivos
UPLOAD_FOLDER = "uploads"
DEFAULT_ZIP_NAME = "archivos_comprimidos"
custom_zip_name = DEFAULT_ZIP_NAME  # Nombre personalizable del ZIP

# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} está online y listo para recibir archivos.")

@bot.command()
async def nombre(ctx, *, nombre: str):
    """Permite al usuario establecer un nombre personalizado para el ZIP."""
    global custom_zip_name
    custom_zip_name = nombre.replace(" ", "_")  # Reemplazar espacios con guiones bajos
    await ctx.send(f"✅ Nombre del ZIP cambiado a: `{custom_zip_name}.zip`")

@bot.command()
async def subir(ctx):
    """Comprime los archivos subidos y envía el ZIP con el nombre personalizado."""
    zip_path = f"{UPLOAD_FOLDER}/{custom_zip_name}.zip"
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)
    await ctx.send(f"📁 Archivo ZIP `{custom_zip_name}.zip` generado:", file=discord.File(zip_path))

@bot.command()
async def subir_extra(ctx):
    """Crea un segundo archivo ZIP para almacenamiento extra."""
    extra_zip_name = "archivos_extra"
    zip_path = f"{UPLOAD_FOLDER}/{extra_zip_name}.zip"
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)
    await ctx.send(f"📁 Archivo ZIP `{extra_zip_name}.zip` generado:", file=discord.File(zip_path))

@bot.command()
async def resetear(ctx):
    """Elimina todos los archivos en la carpeta de subida."""
    for file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        os.remove(file_path)
    await ctx.send("🗑️ Todos los archivos han sido eliminados.")

@bot.command()
async def limpiar(ctx, *, nombre_archivo: str):
    """Elimina un archivo específico por su nombre."""
    file_path = os.path.join(UPLOAD_FOLDER, nombre_archivo)
    if os.path.exists(file_path):
        os.remove(file_path)
        await ctx.send(f"✅ Archivo `{nombre_archivo}` eliminado.")
    else:
        await ctx.send(f"⚠️ No se encontró el archivo `{nombre_archivo}`.")

@bot.event
async def on_message(message):
    """Recibe archivos y los guarda en la carpeta."""
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith((".dff", ".txd")):
                file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
                await attachment.save(file_path)
                await message.channel.send(f"✅ Archivo `{attachment.filename}` guardado correctamente.")
    
    await bot.process_commands(message)

# Ejecutar el bot
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    print("🚨 ERROR: Token inválido. Revisa tu configuración.")
