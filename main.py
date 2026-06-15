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

# Railway Variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ROBLOX_API_KEY = os.getenv("ROBLOX_API_KEY")

UNIVERSE_ID = "558298"
MY_GUILD_ID = 1515815434115481771
MOD_ROLE_ID = 1515815434115481775
LOG_CHANNEL_ID = 1515815434811740173

intents = discord.Intents.default()
intents.message_content = True # Message padhne ki power
bot = commands.Bot(command_prefix="!", intents=intents)

# Load Linked Accounts
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
    print("Bot is LIVE! Verification & Two-Way Chat Enabled 🚀")

# --- TWO-WAY CROSS CHAT (Discord to Roblox) ---
@bot.event
async def on_message(message):
    # Agar message bot ne bheja hai, ya log channel mein nahi hai, toh ignore karo
    if message.author.bot or message.channel.id != LOG_CHANNEL_ID:
        return
    
    links = load_links()
    discord_id = str(message.author.id)
    
    # Agar user link nahi hai, toh use batao
    if discord_id not in links:
        await message.reply("⚠️ Tera account link nahi hai! Pehle `/verify` use kar.", delete_after=5)
        return

    roblox_name = links[discord_id]
    top_role = message.author.top_role.name # Sabse main title uthayega
    
    # Roblox ko message bhejo
    cross_data = {
        "message": json.dumps({
            "Role": top_role,
            "Username": roblox_name,
            "Message": message.content
        })
    }
    requests.post(f"https://apis.roblox.com/messaging-service/v1/universes/{UNIVERSE_ID}/topics/DiscordCrossChat", 
                  headers={"x-api-key": ROBLOX_API_KEY, "Content-Type": "application/json"}, 
                  data=json.dumps(cross_data))
    
    await message.add_reaction("✅") # Message successful bhejne par tick lagayega

# --- VERIFICATION SYSTEM (UI Button) ---
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
        
        # Roblox profile check karo
        r = requests.get(f"https://users.roblox.com/v1/users/{self.roblox_id}")
        desc = r.json().get("description", "")
        
        if self.code in desc:
            save_link(self.discord_id, self.roblox_username)
            await interaction.response.send_message(f"🎉 **Success!** Tera Discord aur Roblox account hamesha ke liye link ho gaya hai as `{self.roblox_username}`!")
            self.stop()
        else:
            await interaction.response.send_message("❌ Code nahi mila! Kya tune 'About' section mein code daal kar save kiya tha?", ephemeral=True)

@bot.tree.command(name="verify", description="Link your Roblox Account securely")
async def slash_verify(interaction: discord.Interaction, roblox_username: str):
    await interaction.response.defer()
    
    # Check if user exists
    r = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_username], "excludeBannedUsers": False})
    data = r.json().get("data")
    if not data:
        await interaction.followup.send("❌ Roblox player nahi mila!")
        return
        
    roblox_id = str(data[0]["id"])
    
    # Generate secret code
    secret_code = "Verify-" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
    
    embed = discord.Embed(title="🔗 Link Roblox Account", color=discord.Color.gold())
    embed.add_field(name="Step 1", value="Apne Roblox Profile mein jao (Settings).", inline=False)
    embed.add_field(name="Step 2", value=f"Apne 'About' (Description) mein ye code paste karo:\n**`{secret_code}`**", inline=False)
    embed.add_field(name="Step 3", value="Save karo aur niche wala button dabao.", inline=False)
    
    view = VerifyView(interaction.user.id, roblox_id, roblox_username, secret_code)
    await interaction.followup.send(embed=embed, view=view)

# --- (PURANI COMMANDS AISE HI RAHENGI: /ban, /unban, /kick, /warn, /announce) ---
# ... TUMHARA PURANA CODE YAHAN RAKH LENA AGAR UPAR WALA REPLACE KAR RAHE HO ...
