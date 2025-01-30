import discord
import os
import shutil
import datetime
import asyncio
from discord.ext import commands

# Obtener el token desde las variables de entorno
TOKEN = os.environ.get("DISCORD_TOKEN")

# Verificar que el token esté disponible
if not TOKEN:
    raise ValueError("🚨 ERROR: No se encontró el token del bot. Asegúrate de configurarlo en Railway.")

# Configurar intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Inicializar bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Carpeta donde se guardarán los archivos
UPLOAD_FOLDER = "uploads"
EXTRA_FOLDER = "extra_uploads"
DEFAULT_NAME = "Modpack"

# Variables globales para el nombre del ZIP
zip_name = DEFAULT_NAME

# Tamaño máximo permitido para el ZIP (MB)
MAX_ZIP_SIZE_MB = 50  

# Crear carpetas si no existen
for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} está online y listo para recibir archivos.")

@bot.command()
async def nombre(ctx, *, nuevo_nombre: str):
    """Asigna un nombre personalizado al archivo ZIP"""
    global zip_name
    zip_name = nuevo_nombre
    await ctx.send(f"✅ Nombre del ZIP actualizado a: `{zip_name}`")

async def crear_zip(folder, zip_name):
    """Crea un archivo ZIP de forma asíncrona"""
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    zip_path = os.path.join(folder, f"{zip_name} {fecha}.zip")
    
    # Verificar tamaño de los archivos antes de comprimir
    total_size = sum(os.path.getsize(os.path.join(folder, f)) for f in os.listdir(folder)) / (1024 * 1024)
    
    if total_size > MAX_ZIP_SIZE_MB:
        return None, f"⚠️ No se puede generar el ZIP: El tamaño total de los archivos es {total_size:.2f} MB y supera el límite de {MAX_ZIP_SIZE_MB} MB."

    # Comprimir en un hilo separado
    await asyncio.to_thread(shutil.make_archive, zip_path.replace(".zip", ""), 'zip', folder)
    
    return zip_path, None

@bot.command()
async def subir(ctx):
    """Comprime los archivos subidos y envía el ZIP"""
    zip_path, error = await crear_zip(UPLOAD_FOLDER, zip_name)
    
    if error:
        await ctx.send(error)
        return

    await ctx.send(f"📁 Archivo ZIP `{os.path.basename(zip_path)}` generado.", file=discord.File(zip_path))

@bot.command()
async def subir_extra(ctx):
    """Comprime los archivos en el ZIP extra y lo envía"""
    zip_path, error = await crear_zip(EXTRA_FOLDER, f"{zip_name}_extra")

    if error:
        await ctx.send(error)
        return

    await ctx.send(f"📁 Archivo ZIP `{os.path.basename(zip_path)}` generado.", file=discord.File(zip_path))

@bot.command()
async def resetear(ctx):
    """Elimina todos los archivos subidos"""
    for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))

    await ctx.send("🗑️ Todos los archivos han sido eliminados.")

@bot.command()
async def limpiar(ctx, filename: str):
    """Elimina un archivo específico"""
    found = False
    for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            found = True
            await ctx.send(f"🗑️ Archivo `{filename}` eliminado correctamente.")
    
    if not found:
        await ctx.send(f"⚠️ No se encontró `{filename}` en los archivos.")

@bot.command()
async def remplazar(ctx, filename: str):
    """Reemplaza un archivo existente con el nuevo adjunto"""
    if not ctx.message.attachments:
        await ctx.send("⚠️ Debes adjuntar un archivo para reemplazarlo.")
        return
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    for attachment in ctx.message.attachments:
        if attachment.filename == filename:
            await attachment.save(file_path)
            await ctx.send(f"♻️ Archivo `{filename}` reemplazado correctamente.")
            return

    await ctx.send(f"⚠️ No se encontró `{filename}` adjunto en tu mensaje.")

@bot.event
async def on_message(message):
    """Recibe archivos y los guarda en la carpeta"""
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
    print("🚨 ERROR: Token inválido. Revisa tu configuración en Railway.")
