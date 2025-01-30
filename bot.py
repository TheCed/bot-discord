import discord
import os
import shutil
import datetime
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

# Inicializar bot sin prefijo, pero con soporte para comandos de barra (/)
bot = commands.Bot(command_prefix=commands.when_mentioned_or(""), intents=intents)

# Carpeta donde se guardarán los archivos
UPLOAD_FOLDER = "uploads"
EXTRA_FOLDER = "extra_uploads"
DEFAULT_NAME = "Modpack"

# Variables globales para el nombre del ZIP
zip_name = DEFAULT_NAME

# Crear carpetas si no existen
for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sincroniza los comandos de barra con Discord
    print(f"✅ {bot.user} está online y listo para recibir archivos.")

@bot.tree.command(name="nombre")
async def nombre(interaction: discord.Interaction, nuevo_nombre: str):
    """Asigna un nombre personalizado al archivo ZIP"""
    global zip_name
    zip_name = nuevo_nombre
    await interaction.response.send_message(f"✅ Nombre del ZIP actualizado a: `{zip_name}`")

@bot.tree.command(name="subir")
async def subir(interaction: discord.Interaction):
    """Comprime los archivos subidos y envía el ZIP"""
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    zip_path = f"{UPLOAD_FOLDER}/{zip_name} {fecha}.zip"

    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)

    await interaction.response.send_message(f"📁 Archivo ZIP `{zip_name} {fecha}.zip` generado.", file=discord.File(zip_path))

@bot.tree.command(name="subir_extra")
async def subir_extra(interaction: discord.Interaction):
    """Comprime los archivos en el ZIP extra y lo envía"""
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    zip_path = f"{EXTRA_FOLDER}/{zip_name}_extra_{fecha}.zip"

    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', EXTRA_FOLDER)

    await interaction.response.send_message(f"📁 Archivo ZIP extra `{zip_name}_extra_{fecha}.zip` generado.", file=discord.File(zip_path))

@bot.tree.command(name="resetear")
async def resetear(interaction: discord.Interaction):
    """Elimina todos los archivos subidos"""
    for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))

    await interaction.response.send_message("🗑️ Todos los archivos han sido eliminados.")

@bot.tree.command(name="limpiar")
async def limpiar(interaction: discord.Interaction, filename: str):
    """Elimina un archivo específico"""
    found = False
    for folder in [UPLOAD_FOLDER, EXTRA_FOLDER]:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            found = True
            await interaction.response.send_message(f"🗑️ Archivo `{filename}` eliminado correctamente.")
            return
    
    if not found:
        await interaction.response.send_message(f"⚠️ No se encontró `{filename}` en los archivos.")

@bot.tree.command(name="remplazar")
async def remplazar(interaction: discord.Interaction, filename: str):
    """Reemplaza un archivo existente con el nuevo adjunto"""
    if not interaction.attachments:
        await interaction.response.send_message("⚠️ Debes adjuntar un archivo para reemplazarlo.")
        return
    
    for attachment in interaction.attachments:
        if attachment.filename == filename:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            await attachment.save(file_path)
            await interaction.response.send_message(f"♻️ Archivo `{filename}` reemplazado correctamente.")
            return

    await interaction.response.send_message(f"⚠️ No se encontró `{filename}` adjunto en tu mensaje.")

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
