import discord
import requests
import json
import hashlib
import base64
import os
import random
import string
from discord.ext import commands
from discord import app_commands

# Tokens and Keys (Railway Variables)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ROBLOX_API_KEY = os.getenv("ROBLOX_API_KEY")

# ⚠️ APNI ASLI UNIVERSE ID KO IS QUOTES KE ANDAR RAKHNA BHAI!
UNIVERSE_ID = "558298"

# Tere Saare IDs
MY_GUILD_ID = 1515815434115481771
MOD_ROLE_ID = 1515815434115481775
LOG_CHANNEL_ID = 1515815434811740173       
CHAT_CHANNEL_ID = 1515986089213427803      
REPORTS_CHANNEL_ID = 1516166803678826536  

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- DATABASE LOGIC ---
def load_links():
    try:
        with open("links.json", "r") as f: return json.load(f)
    except FileNotFoundError: return {}

def save_link(discord_id, roblox_name):
    links = load_links()
    links[str(discord_id)] = roblox_name
    with open("links.json", "w") as f: json.dump(links, f)

# --- HELPER FUNCTIONS ---
async def is_mod(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator: return True
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
    print("Bot is LIVE with Cosmic Nuke & Divine Smite! ⚡☄️")

# --- TWO-WAY CROSS CHAT ---
@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHAT_CHANNEL_ID: return
    links = load_links()
    discord_id = str(message.author.id)
    if discord_id not in links: return
    roblox_name = links[discord_id]
    top_role = message.author.top_role.name 
    cross_data = {"message": json.dumps({"Role": top_role, "Username": roblox_name, "Message": message.content})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCrossChat", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(cross_data))
    await message.add_reaction("✅")

# --- DIVINE SMITE / LIGHTNING COMMAND (NEW! ⚡) ---
@bot.tree.command(name="smite", description="Strike a player with a realistic, high-voltage jagged lightning bolt")
@app_commands.check(is_mod)
async def slash_smite(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Smite", "Username": username, "Mod": interaction.user.name})}
    response = requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    
    if response.status_code in [200, 204]:
        await interaction.followup.send(f"⚡⚡ **DIVINE SMITE CALLED!** Judgment is falling upon `{username}`!")
        await send_log("⚡ Divine Smite Delivered", f"**Target:** {username}\n**Executed By:** {interaction.user.name}\n**Verdict:** Vaporized", discord.Color.blue())
    else:
        await interaction.followup.send("❌ Roblox API Error!")

# --- METEOR NUKE COMMAND ---
@bot.tree.command(name="nuke", description="Launch a massive cosmic meteor strike on a player")
@app_commands.check(is_mod)
async def slash_nuke(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Nuke", "Username": username, "Mod": interaction.user.name})}
    response = requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    if response.status_code in [200, 204]:
        await interaction.followup.send(f"☄️🚀 **COSMIC NUKE LAUNCHED!** Meteor heading towards `{username}`!")
    else:
        await interaction.followup.send("❌ Roblox API Error!")

# --- ALL OTHER SLASH COMMANDS ---
@bot.tree.command(name="jail", description="Arrest and cage a player in jail")
@app_commands.check(is_mod)
async def slash_jail(interaction: discord.Interaction, username: str, reason: str, duration: int = 0):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Jail", "Username": username, "Reason": reason, "Duration": duration, "Mod": interaction.user.name})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"⛓️ **{username} Jailed!**")

@bot.tree.command(name="unjail", description="Release a player from jail")
@app_commands.check(is_mod)
async def slash_unjail(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Unjail", "Username": username})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"🔓 **{username} Released!**")

@bot.tree.command(name="shutdown", description="Shutdown all game servers")
@app_commands.check(is_mod)
async def slash_shutdown(interaction: discord.Interaction, reason: str, time: int = 60):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Reason": reason, "Time": time})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordShutdown", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"🛑 **Global Shutdown Initiated!**")

@bot.tree.command(name="verify", description="Link your Roblox Account")
async def slash_verify(interaction: discord.Interaction, roblox_username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data: return
    roblox_id = str(data[0]["id"])
    secret_code = "Verify-" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
    embed = discord.Embed(title="🔗 Link Roblox Account", color=discord.Color.gold())
    embed.add_field(name="Code", value=f"`{secret_code}`")
    class VerifyView(discord.ui.View):
        def __init__(self, discord_id, roblox_id, roblox_username, code):
            super().__init__(timeout=600)
            self.discord_id, self.roblox_id, self.roblox_username, self.code = discord_id, roblox_id, roblox_username, code
        @discord.ui.button(label="Verify Profile", style=discord.ButtonStyle.green)
        async def check_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.discord_id: return
            r = requests.get(f"https://users.roblox.com/v1/users/{self.roblox_id}")
            if self.code in r.json().get("description", ""):
                save_link(self.discord_id, self.roblox_username)
                await interaction.response.send_message("🎉 Linked successfully!")
            else: await interaction.response.send_message("❌ Code not found!", ephemeral=True)
    await interaction.followup.send(embed=embed, view=VerifyView(interaction.user.id, roblox_id, roblox_username, secret_code))

@bot.tree.command(name="ban", description="Ban player")
@app_commands.check(is_mod)
async def slash_ban(interaction: discord.Interaction, username: str, reason: str = "Rules break"):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data: return
    user_id = str(data[0]["id"])
    ds_url = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=BanList&entryKey={user_id}"
    ban_info = json.dumps({"Reason": reason, "Mod": interaction.user.name})
    md5_hash = base64.b64encode(hashlib.md5(ban_info.encode()).digest()).decode()
    requests.post(ds_url, headers={"x-api-key": ROBLOX_API_KEY, "content-md5": md5_hash}, data=ban_info)
    await interaction.followup.send(f"🚨 {username} banned.")

@bot.tree.command(name="unban", description="Unban player")
@app_commands.check(is_mod)
async def slash_unban(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data: return
    user_id = str(data[0]["id"])
    requests.delete(f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry?datastoreName=BanList&entryKey={user_id}", headers={"x-api-key": ROBLOX_API_KEY})
    await interaction.followup.send(f"✅ {username} unbanned.")

bot.run(DISCORD_TOKEN)
