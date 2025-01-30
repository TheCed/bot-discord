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
    print(f"🔄 Nombre del ZIP cambiado a: {zip_name}")
    await interaction.response.send_message(f"✅ Nombre del ZIP actualizado a: `{zip_name}`")

@bot.tree.command(name="subir")
async def subir(interaction: discord.Interaction):
    await interaction.response.defer()
    
    print("📂 Verificando archivos en 'uploads'...")
    archivos = os.listdir(UPLOAD_FOLDER)
    
    if not archivos:
        print("⚠️ No hay archivos en la carpeta.")
        await interaction.followup.send("⚠️ No hay archivos en `uploads` para comprimir.", ephemeral=True)
        return

    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    zip_path = f"{UPLOAD_FOLDER}/{zip_name} {fecha}.zip"

    try:
        print("📦 Creando archivo ZIP...")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', UPLOAD_FOLDER)
        print("✅ ZIP creado:", zip_path)
        await interaction.followup.send(
            f"📁 Archivo ZIP `{zip_name} {fecha}.zip` generado.",
            file=discord.File(zip_path)
        )
    except Exception as e:
        print("🚨 Error al crear el ZIP:", str(e))
        await interaction.followup.send(f"🚨 Error al comprimir archivos: `{str(e)}`", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"📩 Mensaje recibido: {message.content}")

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith((".dff", ".txd")):
                file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
                await attachment.save(file_path)
                print(f"✅ Archivo guardado: {attachment.filename}")
                await message.channel.send(f"✅ Archivo `{attachment.filename}` guardado correctamente.")
    
    await bot.process_commands(message)

async def main():
    async with bot:
        await bot.start(TOKEN)

try:
    asyncio.run(main())
except discord.errors.LoginFailure:
    print("🚨 ERROR: Token inválido. Revisa tu configuración en Railway.")
