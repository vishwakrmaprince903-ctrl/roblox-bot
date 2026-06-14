import discord
import requests
import json
import hashlib
import base64
import os
from discord.ext import commands
from discord import app_commands

# Railway ke 'Variables' se keys uthane ka tarika
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ROBLOX_API_KEY = os.getenv("ROBLOX_API_KEY")
UNIVERSE_ID = os.getenv("UNIVERSE_ID")
MOD_ROLE_ID = int(os.getenv("MOD_ROLE_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def is_mod(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        return True
    return any(role.id == MOD_ROLE_ID for role in interaction.user.roles)

@bot.event
async def on_ready():
    # Server ID ko bhi variable se utha sakte ho ya yahan hardcode kar sakte ho
    MY_GUILD = discord.Object(id=1515815434115481771)
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print("Bot is 24/7 Ready on Railway!")

@bot.tree.command(name="ban", description="Ban player")
@app_commands.check(is_mod)
async def slash_ban(interaction: discord.Interaction, username: str, reason: str = "Rules break"):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    user_id = str(r.json()["data"][0]["id"])
    
    ds_url = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=BanList&entryKey={user_id}"
    ban_info = json.dumps({"Reason": reason, "Mod": interaction.user.name})
    md5_hash = base64.b64encode(hashlib.md5(ban_info.encode()).digest()).decode()
    requests.post(ds_url, headers={"x-api-key": ROBLOX_API_KEY, "content-md5": md5_hash}, data=ban_info)
    
    msg_data = {"message": json.dumps({"Command": "Ban", "Username": username, "Reason": reason})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"🚨 {username} banned by {interaction.user.name}.")

@bot.tree.command(name="unban", description="Unban player")
@app_commands.check(is_mod)
async def slash_unban(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    user_id = str(r.json()["data"][0]["id"])
    requests.delete(f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=BanList&entryKey={user_id}", headers={"x-api-key": ROBLOX_API_KEY})
    await interaction.followup.send(f"✅ {username} unbanned by {interaction.user.name}.")

@bot.tree.command(name="announce", description="Announce in game")
@app_commands.check(is_mod)
async def slash_announce(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Text": text})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordAnnounce", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"📢 Announced: {text}")

bot.run(DISCORD_TOKEN)
