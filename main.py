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

UNIVERSE_ID = "558298"
MY_GUILD_ID = 1515815434115481771
MOD_ROLE_ID = 1515815434115481775
LOG_CHANNEL_ID = 1515815434811740173

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def is_mod(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        return True
    return any(role.id == MOD_ROLE_ID for role in interaction.user.roles)

async def send_log(title, description, color):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=title, description=description, color=color)
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    MY_GUILD = discord.Object(id=MY_GUILD_ID)
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print("Bot is 24/7 Live with Kick, Warn & Chat Logs!")

# --- BAN COMMAND ---
@bot.tree.command(name="ban", description="Ban a player")
@app_commands.check(is_mod)
async def slash_ban(interaction: discord.Interaction, username: str, reason: str = "Rules break"):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data:
        await interaction.followup.send("❌ Player nahi mila!")
        return
    user_id = str(data[0]["id"])
    
    ds_url = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=BanList&entryKey={user_id}"
    ban_info = json.dumps({"Reason": reason, "Mod": interaction.user.name})
    md5_hash = base64.b64encode(hashlib.md5(ban_info.encode()).digest()).decode()
    requests.post(ds_url, headers={"x-api-key": ROBLOX_API_KEY, "content-md5": md5_hash}, data=ban_info)
    
    msg_data = {"message": json.dumps({"Command": "Ban", "Username": username, "Reason": reason})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    
    await interaction.followup.send(f"🚨 {username} ko ban kar diya gaya hai.")
    await send_log("🚨 Player Banned", f"**Username:** {username}\n**Reason:** {reason}\n**Moderator:** {interaction.user.name}", discord.Color.red())

# --- UNBAN COMMAND ---
@bot.tree.command(name="unban", description="Unban a player")
@app_commands.check(is_mod)
async def slash_unban(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data:
        await interaction.followup.send("❌ Player nahi mila!")
        return
    user_id = str(data[0]["id"])
    
    requests.delete(f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=BanList&entryKey={user_id}", headers={"x-api-key": ROBLOX_API_KEY})
    await interaction.followup.send(f"✅ {username} ko unban kar diya.")
    await send_log("✅ Player Unbanned", f"**Username:** {username}\n**Moderator:** {interaction.user.name}", discord.Color.green())

# --- KICK COMMAND (NEW) ---
@bot.tree.command(name="kick", description="Kick player from server")
@app_commands.check(is_mod)
async def slash_kick(interaction: discord.Interaction, username: str, reason: str = "Rule violation"):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Kick", "Username": username, "Reason": reason})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    
    await interaction.followup.send(f"👢 {username} ko kick kar diya gaya.")
    await send_log("👢 Player Kicked", f"**Username:** {username}\n**Reason:** {reason}\n**Moderator:** {interaction.user.name}", discord.Color.orange())

# --- WARN COMMAND (NEW) ---
@bot.tree.command(name="warn", description="Send warning on player's screen")
@app_commands.check(is_mod)
async def slash_warn(interaction: discord.Interaction, username: str, reason: str = "Warning!"):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Warn", "Username": username, "Reason": reason})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    
    await interaction.followup.send(f"⚠️ {username} ko screen par warning bhej di gayi hai.")
    await send_log("⚠️ Player Warned", f"**Username:** {username}\n**Reason:** {reason}\n**Moderator:** {interaction.user.name}", discord.Color.yellow())

# --- ANNOUNCE COMMAND ---
@bot.tree.command(name="announce", description="Send game announcement")
@app_commands.check(is_mod)
async def slash_announce(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Text": text})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordAnnounce", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"📢 Announcement sent: {text}")

# --- WHITELIST COMMANDS ---
@bot.tree.command(name="whitelist", description="Add player to Whitelist")
@app_commands.check(is_mod)
async def slash_whitelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data:
        await interaction.followup.send("❌ Player nahi mila!")
        return
    user_id = str(data[0]["id"])
    
    ds_url = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=WhitelistStore&entryKey={user_id}"
    wl_info = json.dumps({"Whitelisted": True, "Mod": interaction.user.name})
    md5_hash = base64.b64encode(hashlib.md5(wl_info.encode()).digest()).decode()
    requests.post(ds_url, headers={"x-api-key": ROBLOX_API_KEY, "content-md5": md5_hash}, data=wl_info)
    
    await interaction.followup.send(f"⚪ {username} ko Whitelist kar diya.")
    await send_log("⚪ Player Whitelisted", f"**Username:** {username}\n**Moderator:** {interaction.user.name}", discord.Color.gold())

@bot.tree.command(name="unwhitelist", description="Remove from Whitelist")
@app_commands.check(is_mod)
async def slash_unwhitelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data:
        await interaction.followup.send("❌ Player nahi mila!")
        return
    user_id = str(data[0]["id"])
    
    requests.delete(f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=WhitelistStore&entryKey={user_id}", headers={"x-api-key": ROBLOX_API_KEY})
    await interaction.followup.send(f"❌ {username} ko Whitelist se hata diya.")

bot.run(DISCORD_TOKEN)
