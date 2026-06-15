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
REPORTS_CHANNEL_ID = 1516165426105811096  # ⚠️ YAHAN APNE #game-reports CHANNEL KI ID DAALO!

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- DATABASE LOGIC ---
def load_links():
    try:
        with open("links.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_link(discord_id, roblox_name):
    links = load_links()
    links[str(discord_id)] = roblox_name
    with open("links.json", "w") as f:
        json.dump(links, f)

# --- HELPER FUNCTIONS ---
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
    print("Bot is LIVE with Jail & Police Mod system! 🚓")

# --- TWO-WAY CROSS CHAT ---
@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHAT_CHANNEL_ID:
        return
    
    links = load_links()
    discord_id = str(message.author.id)
    
    if discord_id not in links:
        await message.reply("⚠️ Tera account link nahi hai! Pehle `/verify` use kar.", delete_after=5)
        return

    roblox_name = links[discord_id]
    top_role = message.author.top_role.name 
    
    cross_data = {
        "message": json.dumps({
            "Role": top_role,
            "Username": roblox_name,
            "Message": message.content
        })
    }
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCrossChat", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(cross_data))
    await message.add_reaction("✅")

# --- JAIL COMMAND (NEW) ---
@bot.tree.command(name="jail", description="Arrest and cage a player in jail")
@app_commands.check(is_mod)
async def slash_jail(interaction: discord.Interaction, username: str, reason: str, duration: int = 0):
    await interaction.response.defer()
    
    # Save jail state in Roblox DataStore using API
    # 0 mins means Permanent Jail
    # We send command via MessagingService to capture active server players
    msg_data = {
        "message": json.dumps({
            "Command": "Jail",
            "Username": username,
            "Reason": reason,
            "Duration": duration,
            "Mod": interaction.user.name
        })
    }
    
    response = requests.post(
        f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", 
        headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, 
        data=json.dumps(msg_data)
    )
    
    dur_text = f"{duration} Minutes" if duration > 0 else "Permanent"
    if response.status_code in [200, 204]:
        await interaction.followup.send(f"⛓️ **{username} has been Jailed!**\n**Duration:** {dur_text}\n**Reason:** {reason}")
        await send_log("⛓️ Player Jailed", f"**User:** {username}\n**Reason:** {reason}\n**Duration:** {dur_text}\n**Mod:** {interaction.user.name}", discord.Color.purple())
    else:
        await interaction.followup.send("❌ Roblox API Error!")

# --- UNJAIL COMMAND (NEW) ---
@bot.tree.command(name="unjail", description="Release a player from jail")
@app_commands.check(is_mod)
async def slash_unjail(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    msg_data = {
        "message": json.dumps({
            "Command": "Unjail",
            "Username": username
        })
    }
    
    response = requests.post(
        f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", 
        headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, 
        data=json.dumps(msg_data)
    )
    
    if response.status_code in [200, 204]:
        await interaction.followup.send(f"🔓 **{username} has been set free from jail!**")
        await send_log("🔓 Player Unjailed", f"**User:** {username}\n**Mod:** {interaction.user.name}", discord.Color.blue())
    else:
        await interaction.followup.send("❌ Roblox API Error!")

# --- GLOBAL SERVER SHUTDOWN ---
@bot.tree.command(name="shutdown", description="Shutdown all game servers for an update with a timer")
@app_commands.check(is_mod)
async def slash_shutdown(interaction: discord.Interaction, reason: str, time: int = 60):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Reason": reason, "Time": time})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordShutdown", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"🛑 **Global Shutdown Initiated!** Saare servers {time} seconds mein close ho jayenge.")

# --- ALL OTHER SLASH COMMANDS ---

@bot.tree.command(name="verify", description="Link your Roblox Account")
async def slash_verify(interaction: discord.Interaction, roblox_username: str):
    await interaction.response.defer()
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data:
        await interaction.followup.send("❌ Roblox player nahi mila!")
        return
    roblox_id = str(data[0]["id"])
    secret_code = "Verify-" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
    
    embed = discord.Embed(title="🔗 Link Roblox Account", color=discord.Color.gold())
    embed.add_field(name="Step 1", value="Roblox mein Settings -> About section khol.", inline=False)
    embed.add_field(name="Step 2", value=f"Apne About mein ye code paste kar:\n**`{secret_code}`**", inline=False)
    embed.add_field(name="Step 3", value="Save kar aur niche wala button daba.", inline=False)
    
    class VerifyView(discord.ui.View):
        def __init__(self, discord_id, roblox_id, roblox_username, code):
            super().__init__(timeout=600)
            self.discord_id = discord_id
            self.roblox_id = roblox_id
            self.roblox_username = roblox_username
            self.code = code

        @discord.ui.button(label="Check My Profile", style=discord.ButtonStyle.green)
        async def check_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.discord_id:
                await interaction.response.send_message("❌ Ye tera verification nahi hai!", ephemeral=True)
                return
            r = requests.get(f"https://users.roblox.com/v1/users/{self.roblox_id}")
            desc = r.json().get("description", "")
            if self.code in desc:
                save_link(self.discord_id, self.roblox_username)
                await interaction.response.send_message(f"🎉 **Success!** Tera account link ho gaya hai as `{self.roblox_username}`!")
                self.stop()
            else:
                await interaction.response.send_message("❌ Code nahi mila! Apna 'About' section theek se save kar.", ephemeral=True)
                
    view = VerifyView(interaction.user.id, roblox_id, roblox_username, secret_code)
    await interaction.followup.send(embed=embed, view=view)

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
    await interaction.followup.send(f"🚨 {username} banned.")
    await send_log("🚨 Player Banned", f"**User:** {username}\n**Reason:** {reason}\n**Mod:** {interaction.user.name}", discord.Color.red())

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
    await interaction.followup.send(f"✅ {username} unbanned.")

@bot.tree.command(name="kick", description="Kick player from server")
@app_commands.check(is_mod)
async def slash_kick(interaction: discord.Interaction, username: str, reason: str = "Rule violation"):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Kick", "Username": username, "Reason": reason})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"👢 {username} kicked.")

@bot.tree.command(name="warn", description="Send warning on screen")
@app_commands.check(is_mod)
async def slash_warn(interaction: discord.Interaction, username: str, reason: str = "Warning!"):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Command": "Warn", "Username": username, "Reason": reason})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCommands", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"⚠️ {username} warned.")

@bot.tree.command(name="announce", description="Send announcement")
@app_commands.check(is_mod)
async def slash_announce(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    msg_data = {"message": json.dumps({"Text": text})}
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordAnnounce", headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, data=json.dumps(msg_data))
    await interaction.followup.send(f"📢 Announced: {text}")

bot.run(DISCORD_TOKEN)
